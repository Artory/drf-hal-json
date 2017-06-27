from rest_framework import serializers
from rest_framework.relations import Hyperlink


class HyperlinkedPropertyField(serializers.Field):
    process_value = None

    def __init__(self, **kwargs):
        if 'process_value' in kwargs:
            self.process_value = kwargs.pop('process_value')
        super().__init__(**kwargs)

    def to_representation(self, obj):
        val = self.process_value(obj) if self.process_value else obj
        return Hyperlink(val, val)

    def to_internal_value(self, data):
        raise NotImplementedError()


class ContributeTitleField(serializers.SerializerMethodField):

    def __init__(self, **kwargs):
        self.title_for = kwargs.pop('title_for')
        super().__init__(**kwargs)


class HalHyperlinkedRelatedField(serializers.HyperlinkedRelatedField):

    def __init__(self, **kwargs):
        self.title_field = kwargs.pop('title_field', None)
        super().__init__(**kwargs)

    def to_representation(self, instance):
        val = {'href': super().to_representation(instance)}

        if self.title_field and getattr(instance, self.title_field):
            val['title'] = getattr(instance, self.title_field)

        return val


class HalHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def __init__(self, **kwargs):
        self.title_field = kwargs.pop('title_field', None)
        super().__init__(**kwargs)

    def to_representation(self, instance):
        val = {'href': super().to_representation(instance)}

        if self.title_field and getattr(instance, self.title_field):
            val['title'] = getattr(instance, self.title_field)

        return val
