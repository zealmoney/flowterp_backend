from django.urls import path

from .views import FilterMetadataView, HomepageDataView, RecommendationListView

urlpatterns = [
    path("", RecommendationListView.as_view(), name="recommendation-list"),
    path("homepage/", HomepageDataView.as_view(), name="homepage-data"),
    path("filters/", FilterMetadataView.as_view(), name="filter-metadata"),
]