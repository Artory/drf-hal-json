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
