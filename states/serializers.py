from rest_framework import serializers

from .models import CreativeState


class CreativeStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreativeState
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "intended_use",
            "is_active",
        ]