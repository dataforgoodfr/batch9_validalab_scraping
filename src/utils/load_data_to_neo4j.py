from src.utils.process_data_to_load import *


import pandas as pd

def create_dict(row, graph, nodematch, degree, silent_mode=True):
    """[summary]

    Args:
        row (object): [description]
        graph (object): [description]
        nodematch (object): [description]
        degree (str): [description]
        silent_mode (bool, optional): [description]. Defaults to True.

    Returns:
        int: 1
    """
    Entity_dict = {"D"+degree +"_"+ key : row[key] for key in row.keys()}
    
    labels = nodematch.labels
    print("labels ", labels)
    push_item = dict(Entity_dict, **dict(nodematch))
    print("Item to push ",push_item)
    graph.push(Node(*labels, **push_item))
    return 1 #1

def update_nodematch(entity_type,entity_name,name,Node,graph,nodematch,silent_mode):
    """[summary]

    Args:
        entity_type (str): [description]
        entity_name (str): [description]
        name (str): [description]
        Node (object): [description]
        graph (object): [description]
        nodematch (object): [description]
        silent_mode (bool): [description]

    Returns:
        object: return a node object
    """
    print('Trying to merge the node {}'.format(name))
    if not silent_mode:
        print('new node')
    try:
        if entity_type=='Entity' : 
            nodematch = Node(entity_type, entity_name = name)
        elif entity_type=='Website':
            nodematch = Node(entity_type, site_name = name)
        else:
            nodematch = Node(entity_type, user_name = name)

        nodematch.__primarylabel__ = entity_type
        nodematch.__primarykey__ = entity_name
        graph.merge(nodematch)
        print('Merging the node {}'.format(name))
    except:
        print("could not import ", name)
        nodematch = None
    return nodematch


def create_node(row, graph, entity_type,name,nodematch, silent_mode):
    """[summary]

    Args:
        row (object): [description]
        graph (object): [description]
        entity_type (str): [description]
        name (str): [description]
        nodematch (object): [description]
        silent_mode (bool): [description]

    Returns:
        int: 1
    """
    if not silent_mode:
      print("Creating Node")
      print("Entity Type is {}".format(entity_type))
    if entity_type=='Website'  :
      nodematch=update_nodematch(entity_type=entity_type, entity_name=switch_entity_name(entity_type),name=name,nodematch=nodematch,silent_mode=silent_mode)
      if not silent_mode:
        print("Creating Website Node")
        print("Nodematch is {}".format(nodematch))
      #eventually specific processing for websites
    elif entity_type=='Entity':
      nodematch=update_nodematch(entity_type=entity_type, entity_name=switch_entity_name(entity_type),name=name,nodematch=nodematch,silent_mode=silent_mode)
      #specific processing for Entity
      diploDict = {"Diplo_" + key: row[key] for key in row.keys()}
      labels = nodematch.labels
      pushItem = dict(diploDict, **dict(nodematch))
      graph.push(Node(*labels, **pushItem))
    elif entity_type=='Youtube':
      nodematch=update_nodematch( entity_type=entity_type, entity_name=switch_entity_name(entity_type),name=name,nodematch=nodematch,silent_mode=silent_mode)
      #eventually specific processing for Youtube
    elif entity_type=='socialMedia':
      #specific processing for socialMedia
      socialMedia=get_social_media(name)
      user_name = process_name_sm(socialMedia, row, sm_switcher(socialMedia.lower())['separator'])
      condition = eval(sm_switcher(socialMedia.lower())['condition'])
      if (condition):
          print("cannot create " + socialMedia + " node because of name:", row['label'])
          nodematch = None
      else:
          nodematch=update_nodematch(entity_type=socialMedia,entity_name=switch_entity_name(entity_type),name=user_name,nodematch=nodematch,silent_mode=silent_mode)
        
    else:
      print("Don't know the entity type {}".format(entity_type))
    if not silent_mode:
      print("The nodematch is {}".format(nodematch))
    create_dict(row, graph, nodematch, entity_type)
    return 1



# row, graph, entity_type,name,nodematch=None, silent_mode=True
def create_entity(row, graph, source,nodematch=None,silent_mode=True):
    """[summary]

    Args:
        row (pandas row): [description]
        graph (graph): [description]
        source (str): [description]
        nodematch (node, optional): [description]. Defaults to None.
        silent_mode (bool, optional): [description]. Defaults to True.
    """
    if not silent_mode:
        print(nodematch)
    if source=="hyphe":
        if any([s in row['name'].lower() for s in ['facebook','linkedin','twitter','pinterest']]):
            create_node(row=row,graph=graph,entity_type='socialMedia',name=row['name'],nodematch=nodematch,silent_mode=silent_mode)
        else: 
            create_node(row,graph,'Website',row['name'],nodematch=nodematch,silent_mode=silent_mode)
    elif source=="youtube":
        create_node(row,graph,'Youtube',row['title'],nodematch=nodematch,silent_mode=silent_mode)
    else:
        create_node(row,graph,'Entity',row['nom'],nodematch=nodematch,silent_mode=silent_mode)
