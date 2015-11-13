import json
import ckan.lib.base as base
from ckan.common import _, c, g, request, response
import ckan.logic as logic
import ckan.model as model
import ckanext.hdx_users.controllers.mail_validation_controller as mail_validation_controller


get_action = logic.get_action
check_access = logic.check_access
NotAuthorized = logic.NotAuthorized

class PagesController(base.BaseController):
    def new(self, data=None, errors=None, error_summary=None):
        errors = errors or {}
        data_dict = {'content_type': [{'value': 'empty', 'text': _('Select content type')},
                                      {'value': 'map', 'text': _('Map')},
                                      {'value': 'key-figures', 'text': _('Key Figures')},
                                      {'value': 'interactive-data', 'text': _('Interactive Data')},
                                      {'value': 'data-list', 'text': _('Data List')}]}
        vars = {'data': data, 'data_dict': data_dict, 'errors': errors,
                'error_summary': error_summary, 'action': 'new'}

        if request.POST and 'save_custom_page' in request.params:
            context = {'model': model, 'session': model.Session, 'user': c.user or c.author, 'auth_user_obj': c.userobj}
            try:
                check_access('page_create', context, {})
                #TODO exceptions
            except NotAuthorized:
                return mail_validation_controller.OnbNotAuth
            except Exception, e:
                error_summary = e.error_summary
                return self.error_message(error_summary)
            sections_no = int(request.params.get("hdx_counter"))
            sections = []
            for _i in range(0, sections_no):
                if "field-section-" + str(_i) + "-type" in request.params:
                    section = {
                        "type": request.params.get("field-section-" + str(_i) + "-type"),
                        "data-url": request.params.get("field-section-" + str(_i) + "-data-url"),
                        "title-of-visualization": request.params.get(
                            "field-section-" + str(_i) + "-title-of-visualization"),
                        "max-height": request.params.get("field-section-" + str(_i) + "-max-height"),
                        "description": request.params.get("field-section-" + str(_i) + "-description"),
                        "sources": request.params.get("field-section-" + str(_i) + "-sources"),
                    }
                    sections.append(section)
            page_dict = {
                "name": request.params.get("name"),
                "title": request.params.get("title"),
                "type": request.params.get("type"),
                "description": "",
                "sections": json.dumps(sections),
            }
            get_action('page_create')(context, page_dict)

        return base.render('pages/edit_page.html', extra_vars=vars)

    def edit(self, id):
        return None

    def read(self, type, name):
        return None
