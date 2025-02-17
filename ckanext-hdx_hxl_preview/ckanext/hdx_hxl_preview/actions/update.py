import requests
import six.moves.urllib.parse as urlparse
import logging

import ckan.plugins.toolkit as toolkit
import ckan.model as model

_get_action = toolkit.get_action
_get_or_bust = toolkit.get_or_bust

log = logging.getLogger(__name__)
config = toolkit.config

PROXY_CHECK_PATH = '/hxl-test.json'
RESOURCE_TABULAR_FORMATS = ['xls', 'xlsx', 'csv', 'google sheet']

def _check_has_hxl_tags(url):
    '''
    :param url: url of the file to check for hxl tags
    :type url: str
    :return: True if it has the tags otherwise False
    :rtype: bool
    '''
    ret_val = False

    hxl_proxy_url_parts = urlparse.urlsplit(config.get('hdx.hxlproxy.url'))
    hxl_path = hxl_proxy_url_parts[2] + PROXY_CHECK_PATH if hxl_proxy_url_parts[2] else PROXY_CHECK_PATH
    url_wo_params = urlparse.urlunsplit(list(hxl_proxy_url_parts[0:2]) + [hxl_path,'',''])
    params = {
        'url': url
    }
    log.info("HXL Proxy request url: " + str(url_wo_params) + str(params))
    r = requests.get(url_wo_params, params=params, timeout=60, verify=False)
    log.info("Querying url: {}".format(r.url))

    r.raise_for_status()

    response = r.json()

    if response and response.get('status'):
        ret_val = True
    r.close()
    return ret_val

def _view_already_exists(view_list):
    '''
    :param view_list: lists of view
    :type view_list: list
    :return: view if it exists. Otherwise None.
    :rtype: dict
    '''
    if view_list:
        for view in view_list:
            if view and view.get('view_type') == 'hdx_hxl_preview':
                return view
    return None

def package_hxl_update(context, data_dict):
    '''
    Checks every resource in a dataset to see if it has HXL tags.
    Adds the property "has_hxl_tags" as true on the resources that do.

    :param id:
    :type id: str
    :return: new resource view dict list
    :rtype: list
    '''
    package_id = _get_or_bust(data_dict, 'id')

    package_dict = _get_action('package_show')(context, {'id': package_id})

    new_views = []

    if not package_dict.get('private', True):
            # and 'hxl' in [tag.get('name', '').lower() for tag in package_dict.get('tags', [])]:
        for resource in package_dict.get('resources', []):
            view_list = _get_action('resource_view_list')(context, {'id': resource.get('id')})
            view = _view_already_exists(view_list)
            is_res_tabular_format = resource.get('format', '').lower() in RESOURCE_TABULAR_FORMATS
            if  is_res_tabular_format and _check_has_hxl_tags(resource.get('url', '')):
                if not view:
                    resource_view_dict = {
                        'resource_id': resource.get('id'),
                        'title': 'Quick Charts',
                        'description': '',
                        'view_type': 'hdx_hxl_preview'
                    }
                    new_view = _get_action('resource_view_create')(context, resource_view_dict)
                    new_views.append(new_view)
                # else:
                #     # if there's no hxl_preview_config saved we want to return this view as well.
                #     # This will force the hxl preview edit popup to show up for existing resource with no saved configs
                #     if not (view.get('hxl_preview_config') and json.loads(view.get('hxl_preview_config'))):
                #         new_views.append(view)

            elif view:
                _get_action('resource_view_delete')(context, {'id': view.get('id')})
    vocab = model.Vocabulary.get('Topics')
    vocabulary_id = None
    if vocab:
        vocabulary_id = vocab.id
    if new_views and 'hxl' not in [tag.get('name', '').lower() for tag in package_dict.get('tags', [])] and vocabulary_id:
        package_dict['tags'].append({'name': u'hxl', 'vocabulary_id': vocabulary_id})
        _get_action('package_patch')(context, {'id': package_id, 'tags': package_dict.get('tags')})

    return new_views

