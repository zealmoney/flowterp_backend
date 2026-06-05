from decimal import Decimal, InvalidOperation
from feedback.models import StrainFeedback, normalize_feedback_filters
from collections import defaultdict

from django.db.models import (
    Case,
    DecimalField,
    F,
    OuterRef,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from effects.models import Effect
from states.models import CreativeState
from strains.models import (
    Strain,
    StrainEffect,
    StrainState,
    StrainTerpene,
    StrainType,
)
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
from strains.serializers import StrainListSerializer
from django.db.models import Count

from feedback.services import (
    build_feedback_lookup_with_fallback,
    get_feedback_score_adjustment,
    build_user_preference_profile,
    get_personalization_adjustment,
    compute_feedback_confidence,
    build_user_state_preference_profile,
    get_per_state_adjustment,
)

from feedback.memory_services import (
    build_user_memory_summary,
    get_memory_ranking_adjustment,
)


class RecommendationListView(generics.ListAPIView):
    serializer_class = RecommendedStrainSerializer
    permission_classes = [AllowAny]

    STATE_WEIGHT = Decimal("0.65")
    EFFECT_WEIGHT = Decimal("0.20")
    TERPENE_WEIGHT = Decimal("0.10")
    TIME_OF_DAY_WEIGHT = Decimal("0.05")
    MIN_RESULTS_TARGET = 6

    def build_recommendation_queryset(self, filters):
        queryset = (
            StrainState.objects.select_related("strain", "state")
            .filter(
                strain__is_active=True,
                state__is_active=True,
            )
        )

        state_slug = filters.get("state")
        strain_type = filters.get("strain_type")
        effect_slug = filters.get("effect")
        terpene_slug = filters.get("terpene")
        time_of_day = filters.get("time_of_day")
        min_thc = filters.get("min_thc")
        max_thc = filters.get("max_thc")
        featured_only = filters.get("featured")

        if state_slug:
            queryset = queryset.filter(state__slug__iexact=state_slug)

        if strain_type:
            queryset = queryset.filter(strain__strain_type__iexact=strain_type)

        if featured_only is not None and str(featured_only).lower() in ["true", "1", "yes"]:
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

        if effect_slug:
            queryset = queryset.filter(strain__effects__slug__iexact=effect_slug)

        if terpene_slug:
            queryset = queryset.filter(strain__terpenes__slug__iexact=terpene_slug)

        if effect_slug:
            effect_score_subquery = StrainEffect.objects.filter(
                strain=OuterRef("strain"),
                effect__slug__iexact=effect_slug,
            ).values("score")[:1]
        else:
            effect_score_subquery = StrainEffect.objects.none().values("score")

        if terpene_slug:
            terpene_score_subquery = StrainTerpene.objects.filter(
                strain=OuterRef("strain"),
                terpene__slug__iexact=terpene_slug,
            ).values("prominence")[:1]
        else:
            terpene_score_subquery = StrainTerpene.objects.none().values("prominence")

        queryset = queryset.annotate(
            matched_effect_score=Coalesce(
                Subquery(
                    effect_score_subquery,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                ),
                Value(
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                ),
            ),
            matched_terpene_score=Coalesce(
                Subquery(
                    terpene_score_subquery,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                ),
                Value(
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                ),
            ),
        )

        if time_of_day:
            queryset = queryset.annotate(
                matched_time_of_day_score=Case(
                    When(
                        best_time_of_day__iexact=time_of_day,
                        then=Value(
                            Decimal("1.00"),
                            output_field=DecimalField(max_digits=4, decimal_places=2),
                        ),
                    ),
                    default=Value(
                        Decimal("0.00"),
                        output_field=DecimalField(max_digits=4, decimal_places=2),
                    ),
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
            )
        else:
            queryset = queryset.annotate(
                matched_time_of_day_score=Value(
                    Decimal("0.00"),
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
            )

        queryset = queryset.annotate(
            final_score=(
                F("score")
                * Value(
                    self.STATE_WEIGHT,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
                + F("matched_effect_score")
                * Value(
                    self.EFFECT_WEIGHT,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
                + F("matched_terpene_score")
                * Value(
                    self.TERPENE_WEIGHT,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
                + F("matched_time_of_day_score")
                * Value(
                    self.TIME_OF_DAY_WEIGHT,
                    output_field=DecimalField(max_digits=4, decimal_places=2),
                )
            )
        ).order_by("-final_score", "-score", "strain__name")

        return queryset.distinct()


    def get_queryset(self):
        return self.build_recommendation_queryset(self.get_request_filters())
    
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
            "time_of_day": self.request.query_params.get("time_of_day"),
            "min_thc": self.request.query_params.get("min_thc"),
            "max_thc": self.request.query_params.get("max_thc"),
            "featured": self.request.query_params.get("featured"),
        }

    def list(self, request, *args, **kwargs):
        state_slug = request.query_params.get("state")
        if not state_slug:
            return Response(
                {"detail": "The 'state' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset, applied_filters, fallback_applied, fallback_level = self.get_best_queryset_with_fallback(request)

        state_data = self.get_state_data()

        filter_data = {
            "strain_type": applied_filters.get("strain_type"),
            "effect": applied_filters.get("effect"),
            "terpene": applied_filters.get("terpene"),
            "time_of_day": applied_filters.get("time_of_day"),
            "min_thc": applied_filters.get("min_thc"),
            "max_thc": applied_filters.get("max_thc"),
            "featured": applied_filters.get("featured"),
            "mode": applied_filters.get("mode"),
        }

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)

            return Response(
                {
                    "state": state_data,
                    "filters": filter_data,
                    "fallback_applied": fallback_applied,
                    "fallback_level": fallback_level,
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
                "fallback_applied": fallback_applied,
                "fallback_level": fallback_level,
                "count": len(serializer.data),
                "results": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def get_request_filters(self):
        return {
            "state": self.request.query_params.get("state"),
            "strain_type": self.request.query_params.get("strain_type"),
            "effect": self.request.query_params.get("effect"),
            "terpene": self.request.query_params.get("terpene"),
            "time_of_day": self.request.query_params.get("time_of_day"),
            "min_thc": self.request.query_params.get("min_thc"),
            "max_thc": self.request.query_params.get("max_thc"),
            "featured": self.request.query_params.get("featured"),
            "mode": self.request.query_params.get("mode"),
        }


    def build_fallback_filter_sets(self, filters):
        exact = {**filters}
        no_terpene = {**exact, "terpene": None}
        no_effect = {**no_terpene, "effect": None}
        no_thc = {**no_effect, "min_thc": None, "max_thc": None}
        no_time = {**no_thc, "time_of_day": None}

        return [
            ("exact", exact),
            ("terpene_removed", no_terpene),
            ("effect_removed", no_effect),
            ("thc_removed", no_thc),
            ("time_removed", no_time),
        ]


    def apply_feedback_adjustments(self, queryset, request, filters):
        preference_profile = build_user_preference_profile(request.user)
        feedback_lookup = build_feedback_lookup_with_fallback(request.user, filters)
        memory_summary = build_user_memory_summary(request.user)
        state_profile = build_user_state_preference_profile(
            request.user,
            filters.get("state"),
        )

        confidence = compute_feedback_confidence(request.user)

        for item in queryset:
            feedback_adjustment = get_feedback_score_adjustment(
                item.strain_id,
                feedback_lookup,
                confidence,
            )

            personalization_adjustment = get_personalization_adjustment(
                item.strain,
                preference_profile,
            )

            memory_adjustment = get_memory_ranking_adjustment(
                item.strain,
                memory_summary,
            )

            state_adjustment = get_per_state_adjustment(
                item.strain,
                state_profile,
            )

            item.feedback_adjustment = feedback_adjustment
            item.personalization_adjustment = personalization_adjustment
            item.memory_adjustment = memory_adjustment
            item.state_adjustment = state_adjustment

            item.final_score = (
                (item.final_score or Decimal("0.00"))
                + feedback_adjustment
                + personalization_adjustment
                + memory_adjustment
                + state_adjustment
            )

        queryset.sort(
            key=lambda x: (x.final_score, x.score),
            reverse=True,
        )

        return queryset

    def get_best_queryset_with_fallback(self, request):
        filters = self.get_request_filters()
        filter_sets = self.build_fallback_filter_sets(filters)

        best_queryset = []
        best_filters = filters
        best_level = "exact"

        for level, candidate_filters in filter_sets:
            queryset = list(self.build_recommendation_queryset(candidate_filters))

            if len(queryset) > len(best_queryset):
                best_queryset = queryset
                best_filters = candidate_filters
                best_level = level

            if len(queryset) >= self.MIN_RESULTS_TARGET:
                best_queryset = queryset
                best_filters = candidate_filters
                best_level = level
                break

        best_queryset = self.apply_feedback_adjustments(
            best_queryset,
            request,
            best_filters,
        )

        fallback_applied = best_level != "exact"

        return best_queryset, best_filters, fallback_applied, best_level

    def compute_feedback_consistency(user):
        if not user or not user.is_authenticated:
            return Decimal("1.0")

        qs = StrainFeedback.objects.filter(user=user)

        likes = qs.filter(feedback="like").count()
        dislikes = qs.filter(feedback="dislike").count()

        total = likes + dislikes
        if total == 0:
            return Decimal("1.0")

        balance = abs(likes - dislikes) / total

        # 🎯 balanced users = better signal
        return Decimal("0.7") + Decimal(balance) * Decimal("0.6")

       
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
            "energy-boost",
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

        print("FEATURED STATES FOUND:", [state.slug for state in featured_states])

        response_data = {
            "featured_strains": StrainListSerializer(featured_strains, many=True).data,
            "featured_strains": HomepageStrainSerializer(featured_strains, many=True).data,
            "state_sections": HomepageStateSectionSerializer(state_sections, many=True).data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

        print("RESPONSE KEYS:", response_data.keys())
        print("FEATURED STATES COUNT:", len(response_data["featured_states"]))
        print("FEATURED STATES PAYLOAD:", response_data["featured_states"])


class FilterMetadataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        states = (
            CreativeState.objects
            .filter(is_active=True)
            .annotate(strain_count=Count("state_strain_links"))
            .filter(strain_count__gt=0)
            .order_by("name")
        )
        effects = Effect.objects.filter(is_active=True).order_by("name")
        terpenes = Terpene.objects.filter(is_active=True).order_by("name")

        strain_types = [
            {
                "value": value,
                "label": label,
            }
            for value, label in StrainType.choices
        ]

        time_of_day_options = [
            {"value": "morning", "label": "Morning"},
            {"value": "midday", "label": "Midday"},
            {"value": "afternoon", "label": "Afternoon"},
            {"value": "evening", "label": "Evening"},
            {"value": "night", "label": "Night"},
            {"value": "late-night", "label": "Late Night"},
        ]

        response_data = {
            "states": FilterStateSerializer(states, many=True).data,
            "effects": FilterEffectSerializer(effects, many=True).data,
            "terpenes": FilterTerpeneSerializer(terpenes, many=True).data,
            "strain_types": strain_types,
            "time_of_day_options": time_of_day_options,
        }

        return Response(response_data, status=status.HTTP_200_OK)