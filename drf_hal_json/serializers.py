from collections import defaultdict

from rest_framework.reverse import reverse
from rest_framework.utils.serializer_helpers import ReturnDict

from drf_hal_json import EMBEDDED_FIELD_NAME, LINKS_FIELD_NAME, URL_FIELD_NAME
from drf_hal_json.fields import HalHyperlinkedPropertyField, HalContributeToLinkField, \
    HalHyperlinkedSerializerMethodField
from rest_framework.fields import empty, FileField, ImageField
from rest_framework.relations import HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField, RelatedField
from rest_framework.serializers import BaseSerializer, HyperlinkedModelSerializer, ListSerializer
from rest_framework.utils.field_mapping import get_nested_relation_kwargs


class HalListSerializer(ListSerializer):

    @property
    def data(self):
        # The parent class returns ReturnList
        return ReturnDict(
            {
                LINKS_FIELD_NAME: {
                    URL_FIELD_NAME: {
                        'href': self.build_view_url()
                    }
                },
                EMBEDDED_FIELD_NAME: super(ListSerializer, self).data
            },
            serializer=self
        )

    def build_view_url(self):
        # Deduce the URL of the view from the Model
        model = getattr(self.child.Meta, 'model')
        # Support a Meta attribute for adjusting the base_name
        base_name = getattr(self.child.Meta, 'base_name', None)
        if base_name is None:
            # basic approach from rest_framework.utils.field_mapping.get_detail_view_name
            base_name = '%(model_name)s' % {
                'app_label': model._meta.app_label,
                'model_name': model._meta.object_name.lower()
            }
        view_name = '{}-list'.format(base_name)
        return reverse(view_name, request=self.context['request'])


class HalModelSerializer(HyperlinkedModelSerializer):
    """
    Serializer for HAL representation of django models
    """
    serializer_related_field = HyperlinkedRelatedField
    default_list_serializer = HalListSerializer

    def __init__(self, instance=None, data=empty, **kwargs):
        super(HalModelSerializer, self).__init__(instance, data, **kwargs)
        self.nested_serializer_class = self.__class__
        if data != empty and not LINKS_FIELD_NAME in data:
            data[LINKS_FIELD_NAME] = dict()  # put links in data, so that field validation does not fail

    @classmethod
    def many_init(cls, *args, **kwargs):
        # inject the default into list_serializer_class (if not present)
        meta = getattr(cls, 'Meta', None)
        if meta is None:
            class Meta:
                pass
            meta = Meta
            setattr(cls, 'Meta', meta)
        list_serializer_class = getattr(meta, 'list_serializer_class', None)
        if list_serializer_class is None:
            setattr(meta, 'list_serializer_class', cls.default_list_serializer)
        return super(HalModelSerializer, cls).many_init(*args, **kwargs)

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
        ret = super(HalModelSerializer, self).to_representation(instance)
        resp = defaultdict(dict)

        for field_name in self.link_field_names:
            val = ret.pop(field_name)
            if val is not None:
                resp[LINKS_FIELD_NAME][field_name] = self.build_link_object(val)
                for property_name in self.link_property_fields.get(field_name, []):
                    prop = ret.pop(self.link_property_fields[field_name][property_name])
                    if prop is not None:
                        resp[LINKS_FIELD_NAME][field_name][property_name] = prop

        for field_name in self.embedded_field_names:
            # if a related resource is embedded, it should still
            # get a link in the parent object
            if type(ret[field_name]) == list:
                embed_self = list(filter(lambda x: x is not None, [self._get_url(x) for x in ret[field_name] if x]))
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
        self.link_property_fields = defaultdict(dict)

        for field_name, field in fields.items():
            if self._is_link_field(field):
                self.link_field_names.append(field_name)
            if self._is_link_contribution_field(field):
                self.link_property_fields[field.place_on][field.property_name] = field_name
            elif self._is_embedded_field(field):
                self.embedded_field_names.append(field_name)
        return fields

    @staticmethod
    def _is_link_field(field):
        return (isinstance(field, RelatedField) or
                isinstance(field, ManyRelatedField) or
                isinstance(field, HyperlinkedIdentityField) or
                isinstance(field, HalHyperlinkedPropertyField) or
                isinstance(field, HalHyperlinkedSerializerMethodField) or
                isinstance(field, FileField) or
                isinstance(field, ImageField))

    @staticmethod
    def _is_link_contribution_field(field):
        return isinstance(field, HalContributeToLinkField)

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
