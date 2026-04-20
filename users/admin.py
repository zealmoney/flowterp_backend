from django.contrib import admin
from .models import User, Profile, SavedSetup, RecentFlow


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "updated_at")


@admin.register(SavedSetup)
class SavedSetupAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "updated_at")
    search_fields = ("user__email", "user__username", "name")


@admin.register(RecentFlow)
class RecentFlowAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "source", "last_used_at")
    search_fields = ("user__email", "user__username", "name")
    list_filter = ("source",)