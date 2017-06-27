from collections import defaultdict

from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME, URL_FIELD_NAME
from drf_hal_json.fields import HyperlinkedPropertyField, ContributeTitleField
from rest_framework.fields import empty, FileField, ImageField
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField, RelatedField
from rest_framework.serializers import BaseSerializer, HyperlinkedModelSerializer
from rest_framework.utils.field_mapping import get_nested_relation_kwargs


class HalModelSerializer(HyperlinkedModelSerializer):
    """
    Serializer for HAL representation of django models
    """
    serializer_related_field = HyperlinkedRelatedField

    def __init__(self, instance=None, data=empty, **kwargs):
        super(HalModelSerializer, self).__init__(instance, data, **kwargs)
        self.nested_serializer_class = self.__class__
        if data != empty and not LINKS_FIELD_NAME in data:
            data[LINKS_FIELD_NAME] = dict()  # put links in data, so that field validation does not fail

    def build_link_object(self, val):
        if (type([]) == type(val)):
            return [self.build_link_object(v) for v in val]
        if isinstance(val, dict) and val.get('href', False):
            return val
        return {'href': val}

    def _get_url(self, item):
        try:
            return item.get(LINKS_FIELD_NAME, {}).get(URL_FIELD_NAME)
        except AttributeError:
            return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        resp = defaultdict(dict)

        for field_name in self.link_field_names:
            val = ret.pop(field_name)
            if val is not None:
                resp[LINKS_FIELD_NAME][field_name] = self.build_link_object(val)
                if field_name in self.link_title_field_names:
                    resp[LINKS_FIELD_NAME][field_name]['title'] = ret.pop(self.link_title_field_names[field_name])

        for field_name in self.embedded_field_names:
            # if a related resource is embedded, it should still
            # get a link in the parent object
            if type(ret[field_name]) == list:
                embed_self = [self._get_url(x) for x in ret[field_name] if x]
            else:
                embed_self = self._get_url(ret[field_name])
            if embed_self:
                resp[LINKS_FIELD_NAME][field_name] = embed_self
            resp[EMBEDDED_FIELD_NAME][field_name] = ret.pop(field_name)

        resp = dict(resp, **ret)
        return resp

    def get_fields(self):
        fields = super(HalModelSerializer, self).get_fields()

        self.embedded_field_names = []
        self.link_field_names = []
        self.link_title_field_names = {}

        for field_name, field in fields.items():
            if self._is_link_field(field):
                self.link_field_names.append(field_name)
            if self._is_link_title_field(field):
                self.link_title_field_names[field.title_for] = field_name
            elif self._is_embedded_field(field):
                self.embedded_field_names.append(field_name)
        return fields

    @staticmethod
    def _is_link_field(field):
        return (isinstance(field, RelatedField) or
                isinstance(field, ManyRelatedField) or
                isinstance(field, HyperlinkedIdentityField) or
                isinstance(field, HyperlinkedPropertyField) or
                isinstance(field, FileField) or
                isinstance(field, ImageField))

    @staticmethod
    def _is_link_title_field(field):
        return isinstance(field, ContributeTitleField)

    @staticmethod
    def _is_embedded_field(field):
        return isinstance(field, BaseSerializer)

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """
        class NestedSerializer(HalModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = '__all__'

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
