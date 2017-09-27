from collections import OrderedDict

from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param

from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME


class HalPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        result = OrderedDict()
        links = OrderedDict()
        links[api_settings.URL_FIELD_NAME] = {'href': self.request.build_absolute_uri()}
        if self.get_next_link():
            links['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            links['previous'] = {'href': self.get_previous_link()}
        template_url = replace_query_param(self.request.build_absolute_uri(), self.page_query_param, '_PAGE_')
        links['page'] = {
            'href': template_url.replace('_PAGE_', '{?page}'),  # need this trick because of URL encoding
            'templated': True}
        result[LINKS_FIELD_NAME] = links
        result['count'] = self.page.paginator.count
        result['page_size'] = self.get_page_size(self.request)
        result[EMBEDDED_FIELD_NAME] = {'items': data}
        return Response(result)


class HalCursorPagination(CursorPagination):
    def get_paginated_response(self, data):
        result = OrderedDict()
        links = OrderedDict()
        links[api_settings.URL_FIELD_NAME] = {'href': self.base_url}
        if self.get_next_link():
            links['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            links['previous'] = {'href': self.get_previous_link()}
        result[LINKS_FIELD_NAME] = links
        result[EMBEDDED_FIELD_NAME] = {'items': data}
        return Response(result)
