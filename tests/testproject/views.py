from drf_hal_json.views import HalCreateModelMixin
from rest_framework.viewsets import ModelViewSet

from .models import (AbundantResource, CustomResource, RelatedResource1,
                     RelatedResource2, RelatedResource3, TestResource,
                     URLResource, FileResource)
from .serializers import (AbundantResourceSerializer, CustomResourceSerializer,
                          HyperlinkedPropertySerializer,
                          RelatedResource1Serializer,
                          RelatedResource2Serializer,
                          RelatedResource3Serializer, TestResourceSerializer,
                          FileSerializer)


class CustomResourceViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = CustomResourceSerializer
    queryset = CustomResource.objects.all()


class TestResourceViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = TestResourceSerializer
    queryset = TestResource.objects.all()


class RelatedResource1ViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = RelatedResource1Serializer
    queryset = RelatedResource1.objects.all()


class RelatedResource2ViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = RelatedResource2Serializer
    queryset = RelatedResource2.objects.all()


class RelatedResource3ViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = RelatedResource3Serializer
    queryset = RelatedResource3.objects.all()
    lookup_field = 'name'


class AbundantResourceViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = AbundantResourceSerializer
    queryset = AbundantResource.objects.all()


class URLResourceViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = HyperlinkedPropertySerializer
    queryset = URLResource.objects.all()


class FileResourceViewSet(HalCreateModelMixin, ModelViewSet):
    serializer_class = FileSerializer
    queryset = FileResource.objects.all()
