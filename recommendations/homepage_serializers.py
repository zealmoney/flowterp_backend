from rest_framework import serializers

from states.models import CreativeState
from strains.models import Strain
from .serializers import RecommendedStrainSerializer


class HomepageStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreativeState
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "intended_use",
        ]


class HomepageStrainSerializer(serializers.ModelSerializer):
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
            "is_featured",
        ]


class HomepageStateSectionSerializer(serializers.Serializer):
    state = HomepageStateSerializer()
    top_recommendations = RecommendedStrainSerializer(many=True)