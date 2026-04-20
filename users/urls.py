from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    FlowTerpTokenObtainPairView,
    MeView,
    RegisterView,
    SavedSetupDetailView,
    SavedSetupListCreateView,
    RecentFlowListView,
    RecentFlowTrackView,
    RecentFlowDeleteView,
)

urlpatterns = [
    # Auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", FlowTerpTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", MeView.as_view(), name="me"),

    # Saved setups
    path("saved-setups/", SavedSetupListCreateView.as_view(), name="saved-setup-list-create"),
    path("saved-setups/<int:pk>/", SavedSetupDetailView.as_view(), name="saved-setup-detail"),

    # Recent flows
    path("recent-flows/", RecentFlowListView.as_view(), name="recent-flows-list"),
    path("recent-flows/track/", RecentFlowTrackView.as_view(), name="recent-flows-track"),
    path("recent-flows/<int:pk>/", RecentFlowDeleteView.as_view(), name="recent-flows-delete"),
]