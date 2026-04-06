from rest_framework.routers import DefaultRouter

from .views import CreativeStateViewSet

router = DefaultRouter()
router.register("", CreativeStateViewSet, basename="creative-state")

urlpatterns = router.urls