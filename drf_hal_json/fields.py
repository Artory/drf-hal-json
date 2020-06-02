from rest_framework import serializers
from rest_framework.relations import Hyperlink


class HalIncludeInLinksMixin(object):
    """Mixin to flag a field as needing included in the _links section"""
    pass


class HalPromoteEmbeddedMixin(serializers.BaseSerializer):
    """Mixin to flag a field that should be serialized on the top level of its parent instead of embedded"""


class HalHyperlinkedPropertyField(HalIncludeInLinksMixin, serializers.Field):
    process_value = None

    def __init__(self, **kwargs):
        if 'process_value' in kwargs:
            self.process_value = kwargs.pop('process_value')
        super(HalHyperlinkedPropertyField, self).__init__(**kwargs)

    def to_representation(self, obj):
        val = self.process_value(obj) if self.process_value else obj
        if 'request' in self.context:
            val = self.context['request'].build_absolute_uri(val)
        return Hyperlink(val, val)

    def to_internal_value(self, data):
        raise NotImplementedError()


class HalHyperlinkedSerializerMethodField(HalIncludeInLinksMixin, serializers.SerializerMethodField):
    def __init__(self, **kwargs):
        super(HalHyperlinkedSerializerMethodField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return {'href': super(HalHyperlinkedSerializerMethodField, self).to_representation(obj)}

    def to_internal_value(self, data):
        raise NotImplementedError()


class HalContributeToLinkField(serializers.SerializerMethodField):
    # https://tools.ietf.org/html/draft-kelly-json-hal-08#section-5

    def __init__(self, **kwargs):
        self.property_name = kwargs.pop('property_name', 'title')
        self.place_on = kwargs.pop('place_on')
        super(HalContributeToLinkField, self).__init__(**kwargs)


class HalHyperlinkedRelatedField(HalIncludeInLinksMixin, serializers.HyperlinkedRelatedField):

    def __init__(self, **kwargs):
        self.title_field = kwargs.pop('title_field', None)
        self.templated_field = kwargs.pop('templated_field', None)
        self.type_field = kwargs.pop('type_field', None)
        self.deprecation_field = kwargs.pop('deprecation_field', None)
        self.name_field = kwargs.pop('name_field', None)
        super(HalHyperlinkedRelatedField, self).__init__(**kwargs)

    def to_representation(self, instance):
        val = {'href': super(HalHyperlinkedRelatedField, self).to_representation(instance)}

        if self.title_field and getattr(instance, self.title_field):
            val['title'] = getattr(instance, self.title_field)

        if self.templated_field and getattr(instance, self.templated_field):
            val['templated'] = getattr(instance, self.templated_field)

        if self.type_field and getattr(instance, self.type_field):
            val['type'] = getattr(instance, self.type_field)

        if self.deprecation_field and getattr(instance, self.deprecation_field):
            val['deprecation'] = getattr(instance, self.deprecation_field)

        if self.name_field and getattr(instance, self.name_field):
            val['name'] = getattr(instance, self.name_field)

        return val


class HalHyperlinkedIdentityField(HalIncludeInLinksMixin, serializers.HyperlinkedIdentityField):

    def __init__(self, **kwargs):
        self.title_field = kwargs.pop('title_field', None)
        self.templated_field = kwargs.pop('templated_field', None)
        self.type_field = kwargs.pop('type_field', None)
        self.deprecation_field = kwargs.pop('deprecation_field', None)
        self.name_field = kwargs.pop('name_field', None)
        super(HalHyperlinkedIdentityField, self).__init__(**kwargs)

    def to_representation(self, instance):
        val = {'href': super(HalHyperlinkedIdentityField, self).to_representation(instance)}

        if self.title_field and getattr(instance, self.title_field):
            val['title'] = getattr(instance, self.title_field)

        if self.templated_field and getattr(instance, self.templated_field):
            val['templated'] = getattr(instance, self.templated_field)

        if self.type_field and getattr(instance, self.type_field):
            val['type'] = getattr(instance, self.type_field)

        if self.deprecation_field and getattr(instance, self.deprecation_field):
            val['deprecation'] = getattr(instance, self.deprecation_field)

        if self.name_field and getattr(instance, self.name_field):
            val['name'] = getattr(instance, self.name_field)

        return val


class HalFileField(HalIncludeInLinksMixin, serializers.FileField):
    pass
