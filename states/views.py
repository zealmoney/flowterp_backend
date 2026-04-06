from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import CreativeState
from .serializers import CreativeStateSerializer


class CreativeStateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CreativeState.objects.filter(is_active=True)
    serializer_class = CreativeStateSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"