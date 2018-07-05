from collections import OrderedDict

from rest_framework.pagination import CursorPagination, PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param

from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME


class HalPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        if self.get_next_link():
            data[LINKS_FIELD_NAME]['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            data[LINKS_FIELD_NAME]['previous'] = {'href': self.get_previous_link()}
        template_url = replace_query_param(self.request.build_absolute_uri(), self.page_query_param, '_PAGE_')
        data[LINKS_FIELD_NAME]['page'] = {
            'href': template_url.replace('_PAGE_', '{?page}'),  # need this trick because of URL encoding
            'templated': True}
        data['count'] = self.page.paginator.count
        data['page_size'] = self.get_page_size(self.request)
        return Response(data)


class HalLimitOffsetPagination(LimitOffsetPagination):
    def get_paginated_response(self, data):
        if self.get_next_link():
            data[LINKS_FIELD_NAME]['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            data[LINKS_FIELD_NAME]['previous'] = {'href': self.get_previous_link()}
        template_url = replace_query_param(self.request.build_absolute_uri(), self.limit_query_param, '_PAGE_')
        data[LINKS_FIELD_NAME]['page'] = {
            'href': template_url.replace('_PAGE_', '{?page}'),  # need this trick because of URL encoding
            'templated': True}
        data['count'] = self.count
        data['page_size'] = self.get_limit(self.request)
        return Response(data)


class HalCursorPagination(CursorPagination):
    def get_paginated_response(self, data):
        if self.get_next_link():
            data[LINKS_FIELD_NAME]['next'] = {'href': self.get_next_link()}
        if self.get_previous_link():
            data[LINKS_FIELD_NAME]['previous'] = {'href': self.get_previous_link()}
        return Response(data)
