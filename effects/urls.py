from rest_framework.routers import DefaultRouter

from .views import EffectViewSet

router = DefaultRouter()
router.register("", EffectViewSet, basename="effect")

urlpatterns = router.urls