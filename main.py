from webcrawler import WebCrawler
from graphanalyzer import *

list_url = ["https://stat.huji.ac.il"]
# list_url = ["https://www.accenture.com"]
# list_url = ["https://www.reddit.com"]
# list_url = ["https://www.3m.com", "https://www.aosmith.com", "https://www.abbott.com", "https://www.bnymellon.com"]

depth = 3


def manager():
    # part 1 - web crawler
    web_crawler = WebCrawler(urls=list_url, num_layers=depth)
    web_crawler.populate_db()
    web_crawler.save_result()
    # part 2 - analyze the graph
    data = upload_web_crawler_result()
    graph_analyzer_manager(data=data)


if __name__ == '__main__':
    manager()
