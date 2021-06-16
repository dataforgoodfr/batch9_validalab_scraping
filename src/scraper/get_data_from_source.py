from settings import *
import networkx as nx
import pandas as pd


if __name__ == "__main__":
    # execute only if run as a script
    gexffilepath = DATA_DIR + "\\202005Websites01_D1_DISCO.gexf"
    G = nx.read_gexf(gexffilepath, node_type=None, relabel=False, version='1.1draft')
    data = nx.json_graph.node_link_data(G)

    hyphe_dataframe = pd.json_normalize(data['nodes'])
    media_dataframe = pd.read_csv(DATA_DIR + "\\medias_francais.csv")

    hyphe_list = get_data(hyphe_dataframe, "hyphe", "D1")
    media_list = get_data(media_dataframe, "Diplo", "Diplo_")