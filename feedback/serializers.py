from rest_framework import serializers

from strains.models import Strain
from .models import StrainFeedback, normalize_feedback_filters


class StrainFeedbackReadSerializer(serializers.ModelSerializer):
    strain_id = serializers.IntegerField(source="strain.id", read_only=True)

    class Meta:
        model = StrainFeedback
        fields = [
            "id",
            "strain_id",
            "feedback",
            "filters_json",
            "created_at",
            "updated_at",
        ]


class StrainFeedbackWriteSerializer(serializers.ModelSerializer):
    strain_id = serializers.PrimaryKeyRelatedField(
        source="strain",
        queryset=Strain.objects.all(),
    )

    class Meta:
        model = StrainFeedback
        fields = [
            "id",
            "strain_id",
            "feedback",
            "filters_json",
        ]

    def validate_feedback(self, value):
        if value not in {"like", "dislike"}:
            raise serializers.ValidationError("Feedback must be 'like' or 'dislike'.")
        return value

    def validate_filters_json(self, value):
        return normalize_feedback_filters(value)