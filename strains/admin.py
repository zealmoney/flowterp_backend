from django.contrib import admin

from .models import Strain, StrainEffect, StrainTerpene, StrainState


class StrainEffectInline(admin.TabularInline):
    model = StrainEffect
    extra = 1


class StrainTerpeneInline(admin.TabularInline):
    model = StrainTerpene
    extra = 1


class StrainStateInline(admin.TabularInline):
    model = StrainState
    extra = 1


@admin.register(Strain)
class StrainAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "strain_type",
        "thc_min",
        "thc_max",
        "cbd_min",
        "cbd_max",
        "is_active",
        "is_featured",
        "created_at",
    )
    search_fields = (
        "name",
        "description",
        "flavor_profile",
        "aroma_profile",
        "breeder",
        "lineage",
    )
    list_filter = (
        "strain_type",
        "is_active",
        "is_featured",
        "created_at",
    )
    prepopulated_fields = {"slug": ("name",)}
    inlines = [StrainEffectInline, StrainTerpeneInline, StrainStateInline]


@admin.register(StrainEffect)
class StrainEffectAdmin(admin.ModelAdmin):
    list_display = ("strain", "effect", "score")
    search_fields = ("strain__name", "effect__name", "notes")
    list_filter = ("effect",)


@admin.register(StrainTerpene)
class StrainTerpeneAdmin(admin.ModelAdmin):
    list_display = ("strain", "terpene", "prominence")
    search_fields = ("strain__name", "terpene__name", "notes")
    list_filter = ("terpene",)


@admin.register(StrainState)
class StrainStateAdmin(admin.ModelAdmin):
    list_display = ("strain", "state", "score", "best_time_of_day")
    search_fields = ("strain__name", "state__name", "notes", "best_time_of_day")
    list_filter = ("state", "best_time_of_day")