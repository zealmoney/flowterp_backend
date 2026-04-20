from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import StrainFeedbackViewSet, FlowMemoryView

router = DefaultRouter()
router.register("feedback", StrainFeedbackViewSet, basename="feedback")

urlpatterns = [
    # keep all router routes
    *router.urls,

    # add memory endpoint
    path("me/flow-memory/", FlowMemoryView.as_view(), name="flow-memory"),
]