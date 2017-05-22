from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import CustomResourceViewSet, TestResourceViewSet, \
    RelatedResource1ViewSet, RelatedResource2ViewSet, RelatedResource3ViewSet

router = DefaultRouter()
router.register(r'test-resources', TestResourceViewSet)
router.register(r'related-resources-1', RelatedResource1ViewSet)
router.register(r'related-resources-2', RelatedResource2ViewSet)
router.register(r'related-resources-3', RelatedResource3ViewSet)
router.register(r'custom-resource', CustomResourceViewSet)
urlpatterns = router.urls
