from rest_framework import serializers

from effects.serializers import EffectSerializer
from states.serializers import CreativeStateSerializer
from terpenes.serializers import TerpeneSerializer
from .models import Strain, StrainEffect, StrainState, StrainTerpene


class StrainEffectSerializer(serializers.ModelSerializer):
    effect = EffectSerializer(read_only=True)

    class Meta:
        model = StrainEffect
        fields = [
            "id",
            "effect",
            "score",
            "notes",
        ]


class StrainTerpeneSerializer(serializers.ModelSerializer):
    terpene = TerpeneSerializer(read_only=True)

    class Meta:
        model = StrainTerpene
        fields = [
            "id",
            "terpene",
            "prominence",
            "notes",
        ]


class StrainStateSerializer(serializers.ModelSerializer):
    state = CreativeStateSerializer(read_only=True)

    class Meta:
        model = StrainState
        fields = [
            "id",
            "state",
            "score",
            "best_time_of_day",
            "notes",
        ]


class SimilarStrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = [
            "id",
            "name",
            "slug",
            "strain_type",
            "flavor_profile",
            "aroma_profile",
            "thc_min",
            "thc_max",
            "is_featured",
        ]


class StrainListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strain
        fields = [
            "id",
            "name",
            "slug",
            "strain_type",
            "flavor_profile",
            "aroma_profile",
            "thc_min",
            "thc_max",
            "cbd_min",
            "cbd_max",
            "is_active",
            "is_featured",
        ]


class StrainDetailSerializer(serializers.ModelSerializer):
    strain_effect_links = StrainEffectSerializer(many=True, read_only=True)
    strain_terpene_links = StrainTerpeneSerializer(many=True, read_only=True)
    strain_state_links = StrainStateSerializer(many=True, read_only=True)
    similar_strains = serializers.SerializerMethodField()
    quick_summary = serializers.SerializerMethodField()
    top_state = serializers.SerializerMethodField()
    top_effect = serializers.SerializerMethodField()

    class Meta:
        model = Strain
        fields = [
            "id",
            "name",
            "slug",
            "strain_type",
            "description",
            "flavor_profile",
            "aroma_profile",
            "thc_min",
            "thc_max",
            "cbd_min",
            "cbd_max",
            "breeder",
            "lineage",
            "is_active",
            "is_featured",
            "created_at",
            "updated_at",
            "quick_summary",
            "top_state",
            "top_effect",
            "strain_effect_links",
            "strain_terpene_links",
            "strain_state_links",
            "similar_strains",
        ]

    def get_quick_summary(self, obj):
        top_state = (
            obj.strain_state_links.select_related("state")
            .order_by("-score")
            .first()
        )
        top_effect = (
            obj.strain_effect_links.select_related("effect")
            .order_by("-score")
            .first()
        )
        top_terpene = (
            obj.strain_terpene_links.select_related("terpene")
            .order_by("-prominence")
            .first()
        )

        return {
            "strain_type": obj.strain_type,
            "primary_state": top_state.state.name if top_state else None,
            "primary_effect": top_effect.effect.name if top_effect else None,
            "primary_terpene": top_terpene.terpene.name if top_terpene else None,
            "thc_range": {
                "min": obj.thc_min,
                "max": obj.thc_max,
            },
            "best_time_of_day": top_state.best_time_of_day if top_state else None,
        }

    def get_top_state(self, obj):
        top_state = (
            obj.strain_state_links.select_related("state")
            .order_by("-score")
            .first()
        )
        if not top_state:
            return None

        return {
            "name": top_state.state.name,
            "slug": top_state.state.slug,
            "score": top_state.score,
            "best_time_of_day": top_state.best_time_of_day,
        }

    def get_top_effect(self, obj):
        top_effect = (
            obj.strain_effect_links.select_related("effect")
            .order_by("-score")
            .first()
        )
        if not top_effect:
            return None

        return {
            "name": top_effect.effect.name,
            "slug": top_effect.effect.slug,
            "score": top_effect.score,
        }

    def get_similar_strains(self, obj):
        similar = self.context.get("similar_strains", [])
        return SimilarStrainSerializer(similar, many=True).data