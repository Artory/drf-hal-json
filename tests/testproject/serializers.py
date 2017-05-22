from drf_hal_json.serializers import HalModelSerializer
from .models import TestResource, RelatedResource2, RelatedResource1


class RelatedResource1Serializer(HalModelSerializer):
    class Meta:
        model = RelatedResource1
        fields = ('self', 'name')


class RelatedResource2Serializer(HalModelSerializer):
    class Meta:
        model = RelatedResource2


class TestResourceSerializer(HalModelSerializer):
    related_resource_1 = RelatedResource1Serializer(read_only=True)
    class Meta:
        model = TestResource
        fields = ('self', 'id', 'name', 'related_resource_1', 'related_resource_2')
        depth = 1
