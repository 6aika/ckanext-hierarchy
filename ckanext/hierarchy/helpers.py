import ckan.plugins as p
from pylons import tmpl_context as c

def get_group_tree():
    return p.toolkit.get_action('group_tree')({'type': 'organization'})

def get_group_tree_section():
    return p.toolkit.get_action('group_tree_section')({'id': c.group_dict.id, 'type': c.group_dict.type})
