from rest_framework import serializers

from strains.models import StrainState


class RecommendedStrainSerializer(serializers.ModelSerializer):
    strain_id = serializers.IntegerField(source="strain.id", read_only=True)
    strain_name = serializers.CharField(source="strain.name", read_only=True)
    strain_slug = serializers.CharField(source="strain.slug", read_only=True)
    strain_type = serializers.CharField(source="strain.strain_type", read_only=True)
    description = serializers.CharField(source="strain.description", read_only=True)
    flavor_profile = serializers.CharField(source="strain.flavor_profile", read_only=True)
    aroma_profile = serializers.CharField(source="strain.aroma_profile", read_only=True)
    thc_min = serializers.DecimalField(
        source="strain.thc_min",
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    thc_max = serializers.DecimalField(
        source="strain.thc_max",
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    cbd_min = serializers.DecimalField(
        source="strain.cbd_min",
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    cbd_max = serializers.DecimalField(
        source="strain.cbd_max",
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    breeder = serializers.CharField(source="strain.breeder", read_only=True)
    lineage = serializers.CharField(source="strain.lineage", read_only=True)
    state_name = serializers.CharField(source="state.name", read_only=True)
    state_slug = serializers.CharField(source="state.slug", read_only=True)
    recommendation_score = serializers.DecimalField(
        source="score",
        max_digits=4,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = StrainState
        fields = [
            "strain_id",
            "strain_name",
            "strain_slug",
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
            "state_name",
            "state_slug",
            "recommendation_score",
            "best_time_of_day",
            "notes",
        ]