from drf_hal_json.serializers import HalModelSerializer
from rest_framework import serializers

from .models import AbundantResource, CustomResource, TestResource, RelatedResource1, RelatedResource2, RelatedResource3


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


class RelatedResource3Serializer(HalModelSerializer):
    class Meta:
        model = RelatedResource3


class CustomResourceSerializer(HalModelSerializer):
    related_resource_3 = serializers.HyperlinkedIdentityField(
        read_only=True, view_name='relatedresource3-detail', lookup_field='name')

    class Meta:
        model = CustomResource
        fields = ('self', 'name', 'related_resource_3')


class AbundantResourceSerializer(HalModelSerializer):
    class Meta:
        model = AbundantResource
