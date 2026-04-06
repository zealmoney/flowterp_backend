from django.db.models import Count, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny

from .filters import StrainFilter
from .models import Strain, StrainEffect, StrainState, StrainTerpene
from .serializers import StrainDetailSerializer, StrainListSerializer


class StrainViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = StrainFilter
    search_fields = [
        "name",
        "description",
        "flavor_profile",
        "aroma_profile",
        "breeder",
        "lineage",
    ]
    ordering_fields = [
        "name",
        "created_at",
        "updated_at",
        "thc_min",
        "thc_max",
        "cbd_min",
        "cbd_max",
    ]
    ordering = ["name"]

    def get_queryset(self):
        return (
            Strain.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "strain_effect_links",
                    queryset=StrainEffect.objects.select_related("effect").order_by("-score")
                ),
                Prefetch(
                    "strain_terpene_links",
                    queryset=StrainTerpene.objects.select_related("terpene").order_by("-prominence")
                ),
                Prefetch(
                    "strain_state_links",
                    queryset=StrainState.objects.select_related("state").order_by("-score")
                ),
                "effects",
                "terpenes",
                "states",
            )
            .distinct()
            .order_by("name")
        )

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StrainDetailSerializer
        return StrainListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, "action", None) == "retrieve":
            strain = self.get_object()

            state_ids = strain.states.values_list("id", flat=True)
            effect_ids = strain.effects.values_list("id", flat=True)

            similar_strains = (
                Strain.objects.filter(is_active=True)
                .exclude(id=strain.id)
                .filter(
                    Q(strain_type=strain.strain_type) |
                    Q(states__id__in=state_ids) |
                    Q(effects__id__in=effect_ids)
                )
                .annotate(
                    shared_states=Count("states", filter=Q(states__id__in=state_ids), distinct=True),
                    shared_effects=Count("effects", filter=Q(effects__id__in=effect_ids), distinct=True),
                )
                .order_by("-shared_states", "-shared_effects", "name")
                .distinct()[:4]
            )

            context["similar_strains"] = similar_strains

        return context