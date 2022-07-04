# Web Crawler For Emails With Importance Analysis

The purpose of this mini-project is to get a list of URLs and crawl around
while extracting emails. The result is a table of URLs and their importance. 

The first part of the project is a web crawler (BeautifulSoup, requests),
and the second is a graph analyzer based on the algorithm of page rank
(networkx). 

## 1. Web Crawler
The input of the web crawler is a list of URLs and a network depth
parameter (e.g. 4). In the initial step, the crawler visits the URLs and
extracts emails and hyperlinks. In the n-th step, it visits the
hyperlinks and extracts emails and hyperlinks again and further on
until reaching the number set by the network depth parameter. 

The result are stored with Json file, save on same folder of the script. 

## 2. Graph Analyzer
The graph analysis is done with Page Rank algorithm. The graph is describes
as direct-graph, while the page rank assume un-direct graph. Truth to be told
I'm not sure if that's the best chose, though it's a good start. 

The result are stored with CVS file, save on same folder of the script. 
