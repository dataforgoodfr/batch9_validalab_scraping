import warnings
from py2neo import Graph, Node, Relationship, RelationshipMatcher, RelationshipMatch

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
    """
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