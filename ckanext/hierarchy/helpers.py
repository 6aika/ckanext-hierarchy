import ckan.plugins as p
from pylons import tmpl_context as c
from pylons import config

def get_group_tree():
    return p.toolkit.get_action('group_tree')({'type': 'organization'})

def get_group_tree_section():
    return p.toolkit.get_action('group_tree_section')({'id': c.group_dict.id, 'type': c.group_dict.type})

def show_organizations_without_datasets():
    return True if p.toolkit.asbool(config.get('ckanext.hierarchy.show_organizations_without_datasets')) == True else False
