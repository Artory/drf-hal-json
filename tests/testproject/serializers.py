from drf_hal_json.fields import (HalContributeToLinkField, HalHyperlinkedIdentityField, HalHyperlinkedPropertyField,
                                 HalHyperlinkedRelatedField, HalHyperlinkedSerializerMethodField)
from drf_hal_json.serializers import HalModelSerializer, HalRelatedModelSerializer
from rest_framework import serializers

from .models import (AbundantResource, CustomResource, FileResource, RelatedResource1, RelatedResource2,
                     RelatedResource3, TestResource, URLResource)


class RelatedResource1Serializer(HalRelatedModelSerializer):
    name = HalContributeToLinkField(place_on='self', property_name='title')

    class Meta:
        model = RelatedResource1
        fields = ('self', 'id', 'name', 'active')

    def get_name(self, obj):
        return obj.name


class RelatedResource1NoSelfSerializer(RelatedResource1Serializer):
    class Meta:
        model = RelatedResource1
        fields = ('id', 'name', 'active')


class RelatedResource2Serializer(HalModelSerializer):
    # These related resources are not embedded, just linked
    related_resources = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name='relatedresource1-detail',
        source='related_resources_1')
    related_resources_1 = HalHyperlinkedRelatedField(
        many=True, read_only=True, view_name='relatedresource1-detail',
        title_field='name')
    related_resources_1_noself = RelatedResource1NoSelfSerializer(many=True, source='related_resources_1')

    class Meta:
        model = RelatedResource2
        fields = ('self', 'id', 'name', 'active', 'related_resources', 'related_resources_1',
                  'related_resources_1_noself')


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
    related_resource_2 = RelatedResource2Serializer(read_only=True)
    related_resource_3 = HalHyperlinkedIdentityField(
        read_only=True, view_name='relatedresource3-detail', lookup_field='name')
    custom_link = HalHyperlinkedSerializerMethodField()
    name = HalContributeToLinkField(place_on='related_resource_3', property_name='title')

    class Meta:
        model = CustomResource
        fields = ('self', 'name', 'related_resource_2', 'related_resource_3', 'custom_link')

    def get_name(self, obj):
        return obj.name

    def get_custom_link(self, obj):
        return 'http://www.example.com'


class AbundantResourceSerializer(HalModelSerializer):
    class Meta:
        model = AbundantResource
        fields = ('self', 'name')


class HyperlinkedPropertySerializer(HalModelSerializer):
    url_abs = HalHyperlinkedPropertyField()
    url_rel = HalHyperlinkedPropertyField()
    url_abs_processed = HalHyperlinkedPropertyField(
        source='url_abs',
        process_value=lambda val: val + '?foo=bar')
    url_rel_processed = HalHyperlinkedPropertyField(
        source='url_rel',
        process_value=lambda val: val + '?foo=bar')

    class Meta:
        model = URLResource
        fields = (
            'self',
            'url_abs',
            'url_rel',
            'url_abs_processed',
            'url_rel_processed',
        )


class FileSerializer(HalModelSerializer):
    self_title = HalContributeToLinkField(place_on='self')
    file_title = HalContributeToLinkField(place_on='file')
    file_type = HalContributeToLinkField(place_on='file', property_name='type')
    self_none = HalContributeToLinkField(place_on='self', property_name='none')

    class Meta:
        model = FileResource
        fields = ('self', 'self_title', 'file', 'file_title', 'file_type', 'image', 'self_none')

    def get_self_title(self, obj):
        return str(obj.pk)

    def get_file_title(self, obj):
        return obj.file.name

    def get_file_type(self, obj):
        return 'application/zip'

    def get_self_none(self, obj):
        return None
