from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import Terpene
from .serializers import TerpeneSerializer


class TerpeneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Terpene.objects.filter(is_active=True)
    serializer_class = TerpeneSerializer
    permission_classes = [AllowAny]
    lookup_field = "slug"