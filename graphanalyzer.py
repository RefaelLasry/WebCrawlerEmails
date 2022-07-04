from urllib.parse import urlparse
import networkx as nx
import pandas as pd
import json


def extract_domain(url):
    domain = urlparse(url).netloc
    return domain


def split_data_into_domains(data: dict):
    data_domain_aware = {}
    for url in data.keys():
        domain = extract_domain(url)
        if domain not in data_domain_aware.keys():
            data_domain_aware[domain] = {}
            data_domain_aware[domain][url] = data[url]
        else:
            data_domain_aware[domain][url] = data[url]
    return data_domain_aware


def extract_nodes_and_its_attribute(input_data: dict):
    """
    Get representation of graph as a dict file and return its nodes.

    example of input data:
    {'url_1': {'emails': ['email_1.1', 'email_1.2'], 'list_urls': ['url_2', 'url_3']},
     'url_2': {'emails': ['email_2.1'], 'list_urls': ['url_3']},
      'url_3': {'emails': ['email_3.1'], 'list_urls': ['url_1']}}

    example of list_nodes:
    [('url_1', {'emails': ['email_1.1', 'email_1.2']}),
     ('url_2', {'emails': ['email_2.1']}), ('url_3', {'emails': ['email_3.1']})]
    """
    list_nodes = []
    for key in input_data.keys():
        data_tuple = (key, {'emails': input_data[key]['emails']})
        list_nodes.append(data_tuple)
    return list_nodes


def extract_edges(input_data: dict):
    """
    Get representation of graph as a dict file and return its edges.

    example of list_nodes:
    [('url_1', 'url_2'), ('url_1', 'url_3'), ('url_2', 'url_3'), ('url_3', 'url_1')]
    """
    list_edges = []
    for key in input_data.keys():
        if len(input_data[key]['list_urls']) > 0:
            for url in input_data[key]['list_urls']:
                data_tuple = (key, url)
                list_edges.append(data_tuple)
    return list_edges


def create_graph(list_nodes, list_edges):
    graph = nx.DiGraph()
    graph.add_nodes_from(list_nodes)
    graph.add_edges_from(list_edges)
    return graph


def compute_importance_with_page_rank(graph: nx.DiGraph):
    page_rank_result = nx.pagerank(graph)
    res = pd.DataFrame(index=page_rank_result.keys(), data=page_rank_result.values(), columns=['importance'])
    res.index.name = 'url'
    return res


def add_emails(df, nodes):
    nodes_df = pd.DataFrame.from_records([(x[0], x[1]['emails']) for x in nodes], columns=['url', 'emails'])
    df = df.merge(nodes_df, on='url', how='left')
    return df


def filter_result(res):
    res = res[~res['emails'].isna()]
    mask = res['emails'].apply(lambda x: len(x)) > 0
    res = res[mask]
    res = res.sort_values(by='importance', ascending=False)
    res = res[0:5]
    res = res.reset_index(drop=True)
    return res


def save_result(df):
    df.to_csv('importance_df.csv')


def upload_web_crawler_result():
    with open('web_crawler_result.json', 'r', encoding='utf-8') as f:
        web_crawler_result = json.load(f)
    return web_crawler_result


def create_analysis_per_domain(data):
    list_df = []
    for current_domain in data.keys():
        domain_data = data[current_domain]
        list_nodes = extract_nodes_and_its_attribute(input_data=domain_data)
        list_edges = extract_edges(input_data=domain_data)
        graph = create_graph(list_nodes, list_edges)
        importance_df = compute_importance_with_page_rank(graph=graph)
        importance_df['domain'] = current_domain
        importance_df_with_emails = add_emails(df=importance_df, nodes=list_nodes)
        importance_df_with_emails = filter_result(importance_df_with_emails)
        importance_df_with_emails = importance_df_with_emails[['domain', 'url', 'importance', 'emails']]
        list_df.append(importance_df_with_emails)
    return list_df


def graph_analyzer_manager(data):
    data = split_data_into_domains(data)
    list_df = create_analysis_per_domain(data)
    df = pd.concat(list_df)
    print(df)
    save_result(df)


if __name__ == '__main__':
    input_real_data_example = upload_web_crawler_result()
    graph_analyzer_manager(data=input_real_data_example)

