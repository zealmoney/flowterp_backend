from rest_framework.routers import DefaultRouter

from .views import TerpeneViewSet

router = DefaultRouter()
router.register("", TerpeneViewSet, basename="terpene")

urlpatterns = router.urls