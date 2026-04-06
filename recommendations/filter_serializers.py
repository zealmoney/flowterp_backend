from rest_framework import serializers

from effects.models import Effect
from states.models import CreativeState
from terpenes.models import Terpene


class FilterStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreativeState
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


class FilterEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = [
            "id",
            "name",
            "slug",
            "description",
        ]


class FilterTerpeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terpene
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "aroma_profile",
        ]