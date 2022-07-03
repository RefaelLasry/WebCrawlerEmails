from webcrawler import WebCrawler
from graphanalyzer import *

list_url = ["https://stat.huji.ac.il"]
# list_url = ["https://www.accenture.com"]

depth = 3


def manager():
    web_crawler = WebCrawler(urls=list_url, num_layers=depth)
    web_crawler.populate_db()
    web_crawler.save_result()
    data = upload_web_crawler_result()
    graph_analyzer_manager(data=data)


if __name__ == '__main__':
    manager()
