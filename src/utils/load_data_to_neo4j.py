from src.validalabUtils.neo4jUtils import *


def create_dict(row, json, prefixe, silentMode=True):
    """[summary]

    Args:
        row ([type]): [description]
        json ([type]): [description]
        prefixe ([type]): [description]
        silentMode (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    Entity_dict = {prefixe+"_"+ key : row[key] for key in row.keys()}
    push_item = dict(Entity_dict, **dict(json))
    return push_item


  
def create_node(row,sourcePrefixe, entityType,name, label,silentMode=True):
    """[summary]

    Args:
        row ([type]): [description]
        sourcePrefixe ([type]): [description]
        entityType ([type]): [description]
        name ([type]): [description]
        label ([type]): [description]
        silentMode (bool, optional): [description]. Defaults to True.
    """
    if not silentMode:
        print("Creating Node")
        print("Entity Type is {}".format(entityType))
    json= {}
    if entityType!='socialMedia':
#         if sourcePrefix="ACPM_SiteGP_" or sourcePrefixe="ACPM_SitePro_":
#             json[switch_entity_name(entityType)]=ACPM_db_site_name(row[label])
#         else:
#             json[switch_entity_name(entityType)]=row[label]
        json[switch_entity_name(entityType)]=row[label]
        pushItem=create_dict(row, json,sourcePrefixe)
    else :
        socialMedia=get_social_media(name)
        user_name = process_name_sm(socialMedia, row, sm_switcher(socialMedia.lower())['separator'])
        json[switch_entity_name(entityType)]=user_name
        condition = eval(sm_switcher(socialMedia.lower())['condition'])
        if (condition):
            print("cannot create " + socialMedia + " node because of name:", row[label])
            pushItem = {}
        else:
            pushItem=create_dict(row, json,sourcePrefixe)

    return pushItem



def create_entity(row,source='hyphe',sourcePrefixe='D0',silentMode=True):
    """[summary]

    Args:
        row ([type]): [description]
        source (str, optional): [description]. Defaults to 'hyphe'.
        sourcePrefixe (str, optional): [description]. Defaults to 'D0'.
        silentMode (bool, optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    if not silentMode:
        print(row['name'])
    if source=="hyphe":
        node={}
        if any([s in row['name'].lower() for s in ['facebook','linkedin','twitter','pinterest']]):
            node=create_node(row=row,sourcePrefixe=sourcePrefixe,entityType='socialMedia',name=row['name'],label="name",silentMode=silentMode)
        else:
            node=create_node(row,sourcePrefixe,'Website',row['name'],"name",silentMode)
    elif source=="youtube":
        node=create_node(row,sourcePrefixe,'Youtube',row['title'],"title",silentMode)
    else:
        node=create_node(row,sourcePrefixe,'Entity',row['nom'],"nom",silentMode)
    print(node)
    return node



def get_data(dataframe,source,sourcePrefixe)  :
    """

    Args:
        dataframe:
        source:
        sourcePrefixe:

    Returns:

    """
    list_dict = []
    dataframe.apply(lambda row: list_dict.append(create_entity(row, source, sourcePrefixe)), axis=1)
    return list_dict



    


    

