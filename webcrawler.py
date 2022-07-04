from concurrent.futures import ThreadPoolExecutor
from requests import adapters as adapters
from itertools import compress
import requests
import time
import json
import re

from bs4 import BeautifulSoup
from verify_email import verify_email

THREAD_POOL = 16


class PageContentManyURLs:
    def __init__(self, urls: list):
        self.urls = urls
        self.pages_content = {}
        self.session = requests.Session()
        self.session.mount('https://', adapters.HTTPAdapter(pool_maxsize=THREAD_POOL, max_retries=3, pool_block=True))
        self.res = {}

    def get_one_page_content(self, url):
        # time.sleep(5)
        response = self.session.get(url)
        if 500 <= response.status_code < 600:  # server may be overload
            time.sleep(5)
        return response, url

    def get_all_pages_content(self):
        with ThreadPoolExecutor(max_workers=THREAD_POOL) as executor:
            for response, url in list(executor.map(self.get_one_page_content, self.urls)):
                if response.status_code == 200:
                    self.pages_content[url] = response.content

    @staticmethod
    def get_page_emails(page_content):
        """
        Extract all emails from the url text.
        """
        soup = BeautifulSoup(page_content, 'html.parser')
        emails = re.findall(r'[a-zA-Z\.-]+@[a-zA-Z\.-]+[a-zA-Z\.-]', soup.text)
        if len(emails) > 1:
            mask = verify_email(emails)
            emails = list(compress(emails, mask))
        if len(emails) == 1:
            mask = verify_email(emails)
            emails = list(compress(emails, [mask]))
        return emails

    @staticmethod
    def filter_invalid_urls(urls):
        res = []
        for i in urls:
            if i[0:4] == 'http':
                res.append(i)
        return res

    def get_urls(self, page_content):
        """
        Extract all hyperlinks from the url content.
        """
        list_urls = []
        soup = BeautifulSoup(page_content, 'html.parser')
        for link in soup.find_all('a', href=True):
            if link.has_attr('href'):
                list_urls.append(link['href'])
        list_urls = list(set(list_urls))
        list_urls = self.filter_invalid_urls(list_urls)
        return list_urls

    def get_urls_and_emails(self):
        for url in self.pages_content.keys():
            url_page_content = self.pages_content[url]
            self.res[url] = {}
            self.res[url]['emails'] = self.get_page_emails(page_content=url_page_content)
            self.res[url]['list_urls'] = self.get_urls(page_content=url_page_content)

    def manager(self):
        self.get_all_pages_content()
        self.get_urls_and_emails()


class WebCrawler:
    """
    This class gets a list of urls and a number of layers parameter. The manager of the class goes over the list of
    urls and build the DB by extracting emails and hyperlinks. Following steps are continuing the scraping as the
     numbers of layer parameters. Each url get re-visit and unique url are gathering.
    """
    def __init__(self, urls: list, num_layers: int):
        self.urls = urls
        self.num_layers = num_layers
        self.db = {}

    def populate_db_first_layer(self):
        page_content_many_urls = PageContentManyURLs(urls=self.urls)
        page_content_many_urls.manager()
        result = page_content_many_urls.res
        self.db.update(result)

    def get_unvisited_urls(self):
        visited_urls = list(self.db.keys())
        unvisited_urls = set()
        for url in self.db.keys():
            url_data = self.db[url]
            unvisited_urls = set(url_data['list_urls']) - set(unvisited_urls) - set(visited_urls)
        return list(unvisited_urls)

    def populate_db_n_layer(self):
        """
        Look for unique URLs and visit them.
        """
        for i in range(0, self.num_layers):
            new_urls_to_visit = self.get_unvisited_urls()
            page_content_many_urls = PageContentManyURLs(urls=new_urls_to_visit)
            page_content_many_urls.manager()
            result = page_content_many_urls.res
            self.db.update(result)

    def populate_db(self):
        self.populate_db_first_layer()
        self.populate_db_n_layer()

    def save_result(self):
        with open('web_crawler_result.json', 'w', encoding='utf-8') as f:
            json.dump(self.db, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # web_crawler = WebCrawler(urls=["https://stat.huji.ac.il"], num_layers=4)
    web_crawler = WebCrawler(urls=["https://www.accenture.com"], num_layers=3)
    web_crawler.populate_db()
    web_crawler.save_result()
