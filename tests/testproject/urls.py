from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import (AbundantResourceViewSet, CustomResourceViewSet,
                    RelatedResource1ViewSet, RelatedResource2ViewSet,
                    RelatedResource3ViewSet, TestResourceViewSet,
                    URLResourceViewSet, FileResourceViewSet)

router = DefaultRouter()
router.register(r'test-resources', TestResourceViewSet)
router.register(r'related-resources-1', RelatedResource1ViewSet)
router.register(r'related-resources-2', RelatedResource2ViewSet)
router.register(r'related-resources-3', RelatedResource3ViewSet)
router.register(r'custom-resources', CustomResourceViewSet)
router.register(r'abundant-resources', AbundantResourceViewSet)
router.register(r'url-resources', URLResourceViewSet)
router.register(r'file-resources', FileResourceViewSet)
urlpatterns = router.urls
