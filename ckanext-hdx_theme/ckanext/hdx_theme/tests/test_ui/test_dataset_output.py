'''
Created on May 16, 2014

@author: alexandru-m-g

'''

import unicodedata

import ckan.tests.factories as factories
import ckan.plugins.toolkit as tk
import ckan.lib.helpers as h
import ckan.model as model

import ckanext.hdx_users.model as umodel
import ckanext.hdx_user_extra.model as ue_model

import ckanext.hdx_theme.tests.hdx_test_base as hdx_test_base

from ckanext.hdx_org_group.helpers.static_lists import ORGANIZATION_TYPE_LIST

package = {
    "package_creator": "test function",
    "private": False,
    "dataset_date": "[1960-01-01 TO 2012-12-31]",
    "indicator": "1",
    "caveats": "These are the caveats",
    "license_other": "TEST OTHER LICENSE",
    "methodology": "This is a test methodology",
    "dataset_source": "World Bank",
    "license_id": "hdx-other",
    "name": "test_dataset_1",
    "notes": "This is a test dataset",
    "title": "Test Dataset 1",
    "owner_org": "hdx-test-org",
    "groups": [{"name": "roger"}]
}

organization = {
    'name': 'hdx-test-org',
    'title': 'Hdx Test Org',
    'hdx_org_type': ORGANIZATION_TYPE_LIST[0][1],
    'org_acronym': 'HTO',
    'org_url': 'https://test-org.test',
    'description': 'This is a test organization',
    'users': [{'name': 'testsysadmin'}, {'name': 'janedoe3'}]
}


class TestDatasetOutput(hdx_test_base.HdxBaseTest):
    # loads missing plugins
    @classmethod
    def _load_plugins(cls):
        hdx_test_base.load_plugin('hdx_org_group hdx_package hdx_users hdx_user_extra hdx_theme')

    @classmethod
    def _get_action(cls, action_name):
        return tk.get_action(action_name)

    @classmethod
    def setup_class(cls):
        super(TestDatasetOutput, cls).setup_class()
        umodel.setup()
        ue_model.create_table()

    def test_deleted_badge_appears(self):
        global package
        global organization
        testsysadmin_token = factories.APIToken(user='testsysadmin', expires_in=2, unit=60 * 60)['token']
        dataset_name = package['name']
        context = {'model': model, 'session': model.Session, 'user': 'testsysadmin'}

        self._get_action('organization_create')(context, organization)

        self._get_action('package_create')(context, package)

        page = self._getPackagePage(dataset_name)
        assert not 'Deleted' in page.body, 'Page should not have deleted badge as it was not deleted'

        self._get_action('package_delete')(
            {'model': model, 'session': model.Session, 'user': 'testsysadmin'},
            {'id': dataset_name}
        )

        deleted_page = self._getPackagePage(dataset_name, testsysadmin_token)
        # print deleted_page.response
        assert 'Deleted' in deleted_page.body, 'Page needs to have deleted badge'

    def _getPackagePage(self, package_id, apitoken=None):
        page = None
        url = h.url_for('dataset_read', id=package_id)
        if apitoken:
            page = self.app.get(url, headers={
                'Authorization': unicodedata.normalize('NFKD', apitoken).encode('ascii', 'ignore')})
        else:
            page = self.app.get(url)
        return page
