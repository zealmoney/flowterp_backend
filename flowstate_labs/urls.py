from django.contrib import admin
from django.urls import include, path

from django.http import JsonResponse
from django.db import connection
from strains.models import Strain
from states.models import CreativeState
import os

def db_health(request):
    database_url = os.environ.get("DATABASE_URL", "")

    return JsonResponse({
        "has_database_url": bool(database_url),
        "database_url_host_hint": database_url.split("@")[-1].split("/")[0] if "@" in database_url else "",
        "db_name": connection.settings_dict.get("NAME"),
        "db_host": connection.settings_dict.get("HOST"),
        "strain_count": Strain.objects.count(),
        "state_count": CreativeState.objects.count(),
    })

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/db-health/", db_health),
    
    path("api/", include("users.urls")),
    path("api/strains/", include("strains.urls")),
    path("api/effects/", include("effects.urls")),
    path("api/terpenes/", include("terpenes.urls")),
    path("api/states/", include("states.urls")),
    path("api/recommendations/", include("recommendations.urls")),
    path("api/", include("feedback.urls")),
]