def ACPM_db_site_name(sites_field, ACPM_referential):
    """[summary]

    Args:
        sites_field ([type]): [description]
        ACPM_referential ([type]): [description]

    Returns:
        [type]: [description]
    """
    site_name = ACPM_referential.get(sites_field, sites_field.lower())  # zone à risque
    return site_name

def process_name_sm(sm, node,sep=" /"):
    """A function to sanitize the names of nodes.

    Args:
        sm (str): social media title (ex: facebook, twitter, etc...)
        node (node): the node we want to sanitize the name
        sep (str, optional): the separator used to get the username given the social media. Defaults to " /".

    Returns:
        str: the username of the social media entity
    """
    
 
    if sm in node['label'].lower():
        if len(node['label'].lower().split(" /")) < 2:
            print("I don't create", node['label'].lower())
            user_name=""
        else:
            user_name = node['label'].lower().split(sep)[1]
            user_name = user_name.replace("%20%e2%80%8f","").replace("%40%20%40","").replace("%40suivre%20sur%20twitter:%20%40","")
            user_name = user_name.replace("%20","").replace("%40","").replace("%e2%81%a9","")
            user_name = user_name.replace("%0apour","").replace("%0apou","").replace("%0apo","")
            user_name = user_name.replace("%e2%80%a6","").replace("%e2%80%8e","").replace("%29","")
            user_name = user_name.replace("%21","").replace("%c3%a9","e").replace("%c3%a1","a")
            user_name = user_name.replace("%c3%a9", "e").replace("%26", "et").replace("%27","").replace("%c3%a7", "c").replace("%c3%bb","u")
    else:
      user_name=''
    return user_name
    
def get_social_media(name):
    """[summary]

    Args:
        name (str): [description]

    Returns:
        str: [description]
    """
    if (name.lower().find('twitter') != -1):
        sm = 'twitter'
    elif (name.lower().find('facebook') != -1):
        sm = 'facebook'
    elif (name.lower().find('linkedin') != -1):
        sm = 'linkedin'
    elif (name.lower().find('pinterest') != -1):
        sm = 'pinterest'
    else:
        sm='unknown'
    return sm

def sm_switcher(sm):
    """[summary]

    Args:
        sm (str): [description]

    Returns:
        str: [description]
    """
    switcher={
                "facebook":{'condition':'".php" in user_name or user_name=="name"',
                            'separator':" /"},
                "twitter":{'condition':'"%" in user_name',
                            'separator':" /"},
                "pinterest":{'condition':'user_name=="pin"',
                            'separator':" /"},
                "linkedin":{'condition':'"linkedin" in row["label"].lower() and len(row["label"].lower().split(" /")) < 2',
                            'separator':".../"},
             }
    return switcher.get(sm.lower(),"Not a social media")
def switch_entity_name(entity_type):
    """[summary]

    Args:
        entity_type (str): [description]

    Returns:
        str: [description]
    """
    switcher={
                "entity":'entity_name',
                "website":'site_name',
                "youtube":'user_name',
                "socialmedia":'user_name',
                "wikipedia":'',
             }
    return switcher.get(entity_type.lower(),"Not a social media")