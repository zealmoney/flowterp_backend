from decimal import Decimal, InvalidOperation

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from effects.models import Effect
from states.models import CreativeState
from strains.models import Strain, StrainState, StrainType
from terpenes.models import Terpene
from .filter_serializers import (
    FilterEffectSerializer,
    FilterStateSerializer,
    FilterTerpeneSerializer,
)
from .homepage_serializers import (
    HomepageStateSectionSerializer,
    HomepageStateSerializer,
    HomepageStrainSerializer,
)
from .serializers import RecommendedStrainSerializer


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendedStrainSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = (
            StrainState.objects.select_related("strain", "state")
            .filter(
                strain__is_active=True,
                state__is_active=True,
            )
            .order_by("-score", "strain__name")
        )

        state_slug = self.request.query_params.get("state")
        strain_type = self.request.query_params.get("strain_type")
        effect_slug = self.request.query_params.get("effect")
        terpene_slug = self.request.query_params.get("terpene")
        min_thc = self.request.query_params.get("min_thc")
        max_thc = self.request.query_params.get("max_thc")
        featured_only = self.request.query_params.get("featured")

        if state_slug:
            queryset = queryset.filter(state__slug__iexact=state_slug)

        if strain_type:
            queryset = queryset.filter(strain__strain_type__iexact=strain_type)

        if effect_slug:
            queryset = queryset.filter(strain__effects__slug__iexact=effect_slug)

        if terpene_slug:
            queryset = queryset.filter(strain__terpenes__slug__iexact=terpene_slug)

        if featured_only is not None and featured_only.lower() in ["true", "1", "yes"]:
            queryset = queryset.filter(strain__is_featured=True)

        if min_thc:
            try:
                queryset = queryset.filter(strain__thc_max__gte=Decimal(min_thc))
            except (InvalidOperation, TypeError):
                pass

        if max_thc:
            try:
                queryset = queryset.filter(strain__thc_min__lte=Decimal(max_thc))
            except (InvalidOperation, TypeError):
                pass

        return queryset.distinct()

    def get_state_data(self):
        state_slug = self.request.query_params.get("state")
        if not state_slug:
            return None

        return (
            CreativeState.objects.filter(slug__iexact=state_slug, is_active=True)
            .values("name", "slug", "description", "intended_use")
            .first()
        )

    def get_filter_data(self):
        return {
            "strain_type": self.request.query_params.get("strain_type"),
            "effect": self.request.query_params.get("effect"),
            "terpene": self.request.query_params.get("terpene"),
            "min_thc": self.request.query_params.get("min_thc"),
            "max_thc": self.request.query_params.get("max_thc"),
            "featured": self.request.query_params.get("featured"),
        }

    def list(self, request, *args, **kwargs):
        state_slug = request.query_params.get("state")
        if not state_slug:
            return Response(
                {
                    "detail": "The 'state' query parameter is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(self.get_queryset())
        state_data = self.get_state_data()
        filter_data = self.get_filter_data()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            return Response(
                {
                    "state": state_data,
                    "filters": filter_data,
                    "count": paginated_response.data["count"],
                    "next": paginated_response.data["next"],
                    "previous": paginated_response.data["previous"],
                    "results": paginated_response.data["results"],
                },
                status=status.HTTP_200_OK,
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "state": state_data,
                "filters": filter_data,
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class HomepageDataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        featured_state_slugs = [
            "deep-focus",
            "creative-flow",
            "cinematic-review",
            "energy-boost",
        ]

        featured_states_map = {
            state.slug: state
            for state in CreativeState.objects.filter(
                is_active=True,
                slug__in=featured_state_slugs,
            )
        }

        featured_states = [
            featured_states_map[slug]
            for slug in featured_state_slugs
            if slug in featured_states_map
        ]

        featured_strains = Strain.objects.filter(
            is_active=True,
            is_featured=True,
        ).order_by("name")[:6]

        section_state_slugs = [
            "deep-focus",
            "creative-flow",
            "cinematic-review",
        ]

        state_sections = []

        for slug in section_state_slugs:
            state = featured_states_map.get(slug)

            if not state:
                continue

            recommendations = (
                StrainState.objects.select_related("strain", "state")
                .filter(
                    state=state,
                    strain__is_active=True,
                )
                .order_by("-score", "strain__name")[:4]
            )

            state_sections.append(
                {
                    "state": state,
                    "top_recommendations": recommendations,
                }
            )

        response_data = {
            "featured_states": HomepageStateSerializer(featured_states, many=True).data,
            "featured_strains": HomepageStrainSerializer(featured_strains, many=True).data,
            "state_sections": HomepageStateSectionSerializer(state_sections, many=True).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class FilterMetadataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        states = CreativeState.objects.filter(is_active=True).order_by("name")
        effects = Effect.objects.filter(is_active=True).order_by("name")
        terpenes = Terpene.objects.filter(is_active=True).order_by("name")

        strain_types = [
            {
                "value": value,
                "label": label,
            }
            for value, label in StrainType.choices
        ]

        response_data = {
            "states": FilterStateSerializer(states, many=True).data,
            "effects": FilterEffectSerializer(effects, many=True).data,
            "terpenes": FilterTerpeneSerializer(terpenes, many=True).data,
            "strain_types": strain_types,
        }

        return Response(response_data, status=status.HTTP_200_OK)