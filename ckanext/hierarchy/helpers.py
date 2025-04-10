import ckan.plugins as p
import ckan.model as model
from ckan.common import request
from ckan.plugins.toolkit import g, config


def get_group_tree():
    return p.toolkit.get_action('group_tree')({'type': 'organization'})


def get_group_tree_section():
    data_dict = {
        'id': g.group_dict['id'],
        'type': g.group_dict['type']
    }
    return p.toolkit.get_action('group_tree_section')({}, data_dict)


def show_organizations_without_datasets():
    return True if p.toolkit.asbool(config.get('ckanext.hierarchy.show_organizations_without_datasets')) \
                   is True else False


def group_tree(organizations=[], type_='organization'):
    full_tree_list = p.toolkit.get_action('group_tree')({}, {'type': type_})

    if not organizations:
        return full_tree_list
    else:
        filtered_tree_list = group_tree_filter(organizations, full_tree_list)
        return filtered_tree_list


def group_tree_filter(organizations, group_tree_list, highlight=False):
    # this method leaves only the sections of the tree corresponding to the
    # list since it was developed for the users, all children organizations
    # from the organizations in the list are included
    def traverse_select_highlighted(group_tree, selection=[], highlight=False):
        # add highlighted branches to the filtered tree
        if group_tree['highlighted']:
            # add to the selection and remove highlighting if necessary
            if highlight:
                selection += [group_tree]
            else:
                selection += group_tree_highlight([], [group_tree])
        else:
            # check if there is any highlighted child tree
            for child in group_tree.get('children', []):
                traverse_select_highlighted(child, selection)

    filtered_tree = []
    # first highlights all the organizations from the list in the three
    for group in group_tree_highlight(organizations, group_tree_list):
        traverse_select_highlighted(group, filtered_tree, highlight)

    return filtered_tree


def group_tree_section(id_, type_='organization', include_parents=True,
                       include_siblings=True):
    return p.toolkit.get_action('group_tree_section')(
        {'include_parents': include_parents,
         'include_siblings': include_siblings},
        {'id': id_, 'type': type_, })


def _get_action_name(group_id):
    model_obj = model.Group.get(group_id)
    return "organization_show" if model_obj.is_organization else "group_show"


def group_tree_parents(id_):
    action_name = _get_action_name(id_)
    data_dict = {
        'id': id_,
        'include_dataset_count': False,
        'include_users': False,
        'include_followers': False,
        'include_tags': False
    }
    tree_node = p.toolkit.get_action(action_name)({}, data_dict)
    if (tree_node['groups']):
        parent_id = tree_node['groups'][0]['name']
        parent_node = \
            p.toolkit.get_action(action_name)({}, {'id': parent_id})
        return group_tree_parents(parent_id) + [parent_node]
    else:
        return []


def group_tree_get_longname(id_, default="", type_='organization'):
    action_name = _get_action_name(id_)
    data_dict = {
        'id': id_,
        'include_dataset_count': False,
        'include_users': False,
        'include_followers': False,
        'include_tags': False
    }
    tree_node = p.toolkit.get_action(action_name)({}, data_dict)
    longname = tree_node.get("longname", default)
    if not longname:
        return default
    return longname


def group_tree_highlight(organizations, group_tree_list):
    def traverse_highlight(group_tree, name_list):
        if group_tree.get('name', "") in name_list:
            group_tree['highlighted'] = True
        else:
            group_tree['highlighted'] = False
        for child in group_tree.get('children', []):
            traverse_highlight(child, name_list)

    selected_names = [o.get('name', None) for o in organizations]

    for group in group_tree_list:
        traverse_highlight(group, selected_names)
    return group_tree_list


def get_allowable_parent_groups(group_id):
    if group_id:
        group = model.Group.get(group_id)
        allowable_parent_groups = \
            group.groups_allowed_to_be_its_parent(type=group.type)
    else:
        allowable_parent_groups = model.Group.all(
            group_type=p.toolkit.get_endpoint()[0])
    return allowable_parent_groups


def is_include_children_selected():
    include_children_selected = False

    if p.toolkit.check_ckan_version(min_version="2.10"):
        is_flask = True
    else:
        from ckan.common import is_flask_request
        is_flask = is_flask_request()

    if is_flask:
        if request.args.get('include_children'):
            include_children_selected = True
    return include_children_selected
