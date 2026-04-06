from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Effect
from .serializers import EffectSerializer


class EffectViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Effect.objects.filter(is_active=True)
    serializer_class = EffectSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"