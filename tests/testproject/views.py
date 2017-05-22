from rest_framework.viewsets import ModelViewSet

from drf_hal_json.views import HalCreateModelMixin
from .models import CustomResource, TestResource, RelatedResource2, RelatedResource1, RelatedResource3
from .serializers import CustomResourceSerializer, TestResourceSerializer, \
    RelatedResource1Serializer, RelatedResource2Serializer, RelatedResource3Serializer


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
