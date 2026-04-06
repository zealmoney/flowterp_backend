from rest_framework import serializers

from .models import Terpene


class TerpeneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terpene
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "aroma_profile",
            "is_active",
        ]