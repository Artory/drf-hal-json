from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import TestResourceViewSet, RelatedResource1ViewSet, RelatedResource2ViewSet

router = DefaultRouter()
router.register(r'test-resources', TestResourceViewSet)
router.register(r'related-resources-1', RelatedResource1ViewSet)
router.register(r'related-resources-2', RelatedResource2ViewSet)
urlpatterns = router.urls
