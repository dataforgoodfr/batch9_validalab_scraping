import pandas as pd
from urllib.parse import urlparse
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

version_info = "v1.15.2"
version_type = 'validalab-scraping'


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


def get_node_info(url, silent_mode=True, marker_id=None):
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


def add_node_info(data, url_column='link'):
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
