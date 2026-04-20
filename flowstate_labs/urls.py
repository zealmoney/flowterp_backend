from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/", include("users.urls")),
    path("api/strains/", include("strains.urls")),
    path("api/effects/", include("effects.urls")),
    path("api/terpenes/", include("terpenes.urls")),
    path("api/states/", include("states.urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/", include("feedback.urls")),
]