from drf_hal_json.serializers import HalModelSerializer
from .models import TestResource, RelatedResource2, RelatedResource1


class RelatedResource1Serializer(HalModelSerializer):
    class Meta:
        model = RelatedResource1
        fields = ('self', 'id', 'name', 'active')


class RelatedResource2Serializer(HalModelSerializer):
    # use nested serializer to control what fields are in the serialized, nested object
    # (specifically we want 'id' to be included, which is not the default)
    related_resources_1 = RelatedResource1Serializer(read_only=True, many=True)

    class Meta:
        model = RelatedResource2
        fields = ('self', 'id', 'name', 'active', 'related_resources_1')


class TestResourceSerializer(HalModelSerializer):
    related_resource_1 = RelatedResource1Serializer(read_only=True)
    related_resource_2 = RelatedResource2Serializer(read_only=True)

    class Meta:
        model = TestResource
        fields = ('self', 'id', 'name', 'related_resource_1', 'related_resource_2')
