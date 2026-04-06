import django_filters

from .models import Strain, StrainType


class StrainFilter(django_filters.FilterSet):
    strain_type = django_filters.ChoiceFilter(choices=StrainType.choices)
    is_featured = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    min_thc = django_filters.NumberFilter(field_name="thc_max", lookup_expr="gte")
    max_thc = django_filters.NumberFilter(field_name="thc_min", lookup_expr="lte")

    min_cbd = django_filters.NumberFilter(field_name="cbd_max", lookup_expr="gte")
    max_cbd = django_filters.NumberFilter(field_name="cbd_min", lookup_expr="lte")

    effect = django_filters.CharFilter(field_name="effects__slug", lookup_expr="iexact")
    terpene = django_filters.CharFilter(field_name="terpenes__slug", lookup_expr="iexact")
    state = django_filters.CharFilter(field_name="states__slug", lookup_expr="iexact")

    class Meta:
        model = Strain
        fields = [
            "strain_type",
            "is_featured",
            "is_active",
            "effect",
            "terpene",
            "state",
        ]