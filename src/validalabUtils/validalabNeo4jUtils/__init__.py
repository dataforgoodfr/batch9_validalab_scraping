import pandas as pd
from urllib.parse import urlparse
import warnings
from graphio import NodeSet, RelationshipSet

warnings.simplefilter(action='ignore')

version_info = "v1.17"
version_type = 'validalab-scraping'


def push_relations(
        graph,
        name_of_relation,
        source_type,
        source_property,
        source_metadata,
        target_list,
        silent_mode=True
):
    """[summary]

    Args:
        name_of_relation ([type]): Nom de la relation ajouter
        source_type ([type]): Type du noeud source de la relation
        source_property ([type]): Nom de la propriété de merge de la source(Merge Key)
        source_metadata ([type]): {'meaning': 'définition', 'weigth':'poids', 'source':'url de la source'}
        target_list ([type]): Liste des url cibles à ajouter
        graph:
        silent_mode:
    """

    # ajouter la source de recommandation à la base de données
    # récupérer les métadonnées de la source via son url
    source_data = get_entity_name(source_metadata['source'])
    if type(target_list) is not list:
        target_list = [target_list]
    if not silent_mode:
        print("------------------------------- CREATING SOURCE NODES -------------------------------")
        # créer un noeud d'enregistrement pour la source
    source_node = NodeSet([source_type], merge_keys=[source_property])
    # ajouter et pousser le noeud de la source dans la base de données
    add_node_if_not_existing(graph, source_property, source_data['name'], source_data['type'], source_node, silent_mode)
    if not silent_mode:
        print("------------------------------- GETTING TARGETS DATA -------------------------------")
        # ré
    target_metadata = [get_entity_name(entity) for entity in target_list]
    # récupérer les données des cibles
    target_data = pd.DataFrame.from_dict(target_metadata)
    if not silent_mode:
        print("1- DataFrame\n ", target_data.head())
    # récupérer les types de cibles (Website, Facebook, Twitter, etc..)
    target_types = target_data.groupby('type').groups.keys()
    if not silent_mode:
        print("2- Targets types ", target_types)
    # créer des listes Nodes pour réaliser des merges groupés
    relations = {}
    target_nodes = {}
    # itérer les types de cibles existants
    if not silent_mode:
        print("------------------------------- CREATING TARGETS NODES -------------------------------")
    for target_type in target_types:
        target_property = switch_entity_name(target_type)
        target_nodes[target_type] = NodeSet([target_type], merge_keys=[target_property])
        relations[target_type] = RelationshipSet(name_of_relation,
                                                [source_type], [target_type],
                                                [source_property], [target_property])

        target_dataframes = target_data.groupby('type').get_group(target_type)
        target_dataframes.apply(lambda row: add_node_if_not_existing(graph, target_property, row['name'], target_type,
                                                                    target_nodes[target_type], silent_mode), axis=1)
        target_dataframes.apply(lambda row: relations[target_type].add_relationship({source_property: source_data['name']},
                                                                                  {target_property: row['name']},
                                                                                  source_metadata), axis=1)
    if not silent_mode:
        print("------------------------------- MERGING NODES -------------------------------")
    for target_type in target_nodes:
        if not silent_mode:
            print("Merging nodes for target type", target_type)
        # target_nodes[target_type].merge(graph)
    if not silent_mode:
        print("------------------------------- MERGING RELATIONS -------------------------------")
    for target_type in relations.keys():
        if not silent_mode:
            print("Merging relations for target type", target_type)
        # relations[target_type].merge(graph)
    return True


def switch_entity_name(entity_type):
    """[summary]
    Args:
        entity_type (str): [description]
    Returns:
        str: [description]
    """
    switcher = {
        "entity": 'entity_name',
        "website": 'site_name',
        "youtube": 'user_name',
        "socialmedia": 'user_name',
        "facebook": 'user_name',
        "twitter": "user_name",
        "instagram": "user_name",
        "wikipedia": '',
        "default": "name"
    }
    return switcher.get(entity_type.lower(), "Not a social media")


def get_entity_name(link):
    from urllib.parse import urlparse
    """Deprecated : kept for retro-compatibility
    """
    if 'facebook' in link.lower() or 'fb.' in link.lower():
        entity_name = link.split('/')[3].split('?')[0].lower()
        entity_address = link.split('?')[0].lower().replace("www.", '').lower()
        entity_type = "Facebook"
    elif 'twitter' in link.lower():
        entity_name = link.split('/')[3].split('?')[0].lower()
        entity_address = link.split('?')[0].lower()
        entity_type = 'Twitter'
    else:
        if len(link.split('/')) < 2:
            entity_name = link.lower().replace("www.", '')
            parsed_uri = urlparse(link)  # returns six components
            entity_address = 'https:' + '//' + link.lower()

        else:
            entity_name = link.split('/')[2].split('?')[0].lower().replace("www.", '')
            parsed_uri = urlparse(link)  # returns six components
            entity_address = link.split('/')[0] + '//' + link.split('/')[2]
        #         '{uri.netloc}/'.format(uri=parsed_uri).split('/')[0].lower()
        entity_type = 'Website'
    return {'name': entity_name, 'address': entity_address, 'type': entity_type}


def get_node_information(url, silent_mode=True, marker_id=None):
    """
    """
    if pd.isnull(url):
        if not silent_mode:
            print('empty link', marker_id)
        return pd.Series({'nodeName': None, 'profileURL': None, 'nodeType': None, 'nodeExtra': None})
    url = url.lower()
    if 'facebook' in urlparse(url).netloc or 'fb.' in urlparse(url).netloc:
        node_name = urlparse(url).path.split('/')[1].split('?')[0]
        node_address = url.split('?')[0]
        node_type = "Facebook"
        node_extra = "None"
    elif 'twitter' in urlparse(url).netloc:
        node_name = urlparse(url).path.split('/')[1].split('?')[0]
        node_address = url.split('?')[0]
        node_type = 'Twitter'
        node_extra = "None"
    elif 'linkedin' in urlparse(url).netloc:
        try:
            node_name = urlparse(url).path.split('/')[2].split('?')[0]
            node_extra = urlparse(url).path.split('/')[1]
        except:
            node_name = "error"
            node_extra = "error"
        node_address = url.split('?')[0]
        node_type = 'Linkedin'

    elif 'youtube' in urlparse(url).netloc:
        if urlparse(url).path.split('/')[1] == 'user' or urlparse(url).path.split('/')[1] == "c" or \
                urlparse(url).path.split('/')[1] == 'channel':
            node_name = urlparse(url).path.split('/')[2].split('?')[0]
            node_address = url.split('?')[0]
            node_type = 'Youtube'
            node_extra = urlparse(url).path.split('/')[1]
        else:
            node_name = urlparse(url).path.split('/')[1].split('?')[0]
            node_address = url.split('?')[0]
            node_type = 'Youtube'
            node_extra = 'page'
    else:
        if len(url.split('/')) < 2:
            node_name = url.replace("www.", '')
            parsed_uri = urlparse(url)  # returns six components
            node_address = 'https:' + '//' + url

        else:
            node_name = url.split('/')[2].split('?')[0].replace("www.", '')
            parsed_uri = urlparse(url)  # returns six components
            node_address = url.split('/')[0] + '//' + url.split('/')[2]
        #         '{uri.netloc}/'.format(uri=parsed_uri).split('/')[0].lower()
        node_type = 'Website'
        node_extra = None
    return pd.Series(
        {'nodeName': node_name, 'profileURL': node_address, 'nodeType': node_type, 'nodeExtra': node_extra}
    )


def add_node_information(data, url_column='link'):
    """ add node information from a dataset containing urls"""
    return data.merge(data.apply(lambda row: get_node_information(url=row[url_column]), axis=1), left_index=True,
                      right_index=True)


def find_node(graph, entity_type, merge_key, property_name):
    """Fonction permettant de retrouver un noeud

    Args:
        entity_type ([type]): [description]
        merge_key ([type]): [description]
        property_name ([type]): [description]

    Returns:
        [type]: [description]
    """
    return graph.nodes.match(entity_type).where("_." + merge_key + " =~ '" + property_name + "'").first()


def create_and_add_node(graph, entity_type, merge_key, property_name, node=None, silentMode=True):
    """Fonction permettant de créer et ajouter noeud

    Args:
        graph ([type]): [description]
        entity_type ([type]): [description]
        merge_key ([type]): [description]
        property_name ([type]): [description]
        node ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """
    from graphio import NodeSet, RelationshipSet
    if not silentMode:
        print("Node: ", node)
    if node == None:
        node = NodeSet([entity_type], merge_keys=[merge_key])
        node.add_node({merge_key: property_name})
        if not silentMode:
            print("Node is not provided for ", property_name)
        print(node, property_name)
    else:
        node.add_node({merge_key: property_name})
        if not silentMode:
            print("A Node is provided for ", property_name)
    node.merge(graph)
    if not silentMode:
        print("Graph is merged")
    return node


def add_node_if_not_existing(graph, merge_key, property_name, entity_type, node=None, silentMode=True):
    """Fonction permettant de créer et ajouter un noeud s'il est inexistant

    Args:
        graph ([type]): [description]
        merge_key ([type]): [description]
        property_name ([type]): [description]
        entity_type ([type]): [description]
        node ([type], optional): [description]. Defaults to None.
    """
    if find_node(graph, entity_type, merge_key, property_name):
        if not silentMode:
            print("The node {} is already existing.".format(property_name))
        pass
    else:
        if not silentMode:
            print("The node {} is not existing.".format(property_name))
        create_and_add_node(graph, entity_type, merge_key, property_name, node, silentMode)