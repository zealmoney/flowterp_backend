from django.contrib import admin

from .models import Terpene


@admin.register(Terpene)
class TerpeneAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "aroma_profile", "is_active")
    search_fields = ("name", "description", "aroma_profile")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}