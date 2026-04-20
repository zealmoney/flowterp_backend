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
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = Strain
        fields = [
            "id",
            "name",
            "slug",
            "strain_type",
            "image_url",
            "flavor_profile",
            "aroma_profile",
            "thc_min",
            "thc_max",
            "cbd_min",
            "cbd_max",
            "is_featured",
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class HomepageStateSectionSerializer(serializers.Serializer):
    state = HomepageStateSerializer()
    top_recommendations = RecommendedStrainSerializer(many=True)