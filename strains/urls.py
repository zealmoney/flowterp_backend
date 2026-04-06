from rest_framework.routers import DefaultRouter

from .views import StrainViewSet

router = DefaultRouter()
router.register("", StrainViewSet, basename="strain")

urlpatterns = router.urls