from django.contrib import admin

from .models import CreativeState


@admin.register(CreativeState)
class CreativeStateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "intended_use", "is_active")
    search_fields = ("name", "description", "intended_use")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}