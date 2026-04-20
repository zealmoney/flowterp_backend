from django.conf import settings
from django.db import models

from strains.models import Strain


def normalize_feedback_filters(filters):
    source = dict(filters or {})
    source.pop("page", None)

    return {
        "state": source.get("state") or "",
        "effect": source.get("effect") or "",
        "terpene": source.get("terpene") or "",
        "time_of_day": source.get("time_of_day") or "",
        "strain_type": source.get("strain_type") or "",
        "featured": bool(source.get("featured")),
        "min_thc": source.get("min_thc") or "",
        "max_thc": source.get("max_thc") or "",
        "mode": source.get("mode") or "sharp",
    }


def build_feedback_signature(strain_id, filters):
    normalized = normalize_feedback_filters(filters)

    return "|".join(
        [
            str(strain_id or ""),
            normalized["state"],
            normalized["effect"],
            normalized["terpene"],
            normalized["time_of_day"],
            normalized["strain_type"],
            "1" if normalized["featured"] else "0",
            str(normalized["min_thc"]),
            str(normalized["max_thc"]),
            normalized["mode"],
        ]
    )


class StrainFeedback(models.Model):
    FEEDBACK_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="strain_feedback",
    )
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="feedback_entries",
    )
    feedback = models.CharField(max_length=10, choices=FEEDBACK_CHOICES)
    filters_json = models.JSONField(default=dict, blank=True)
    filters_signature = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "strain", "filters_signature"],
                name="unique_user_strain_feedback_per_filter_context",
            )
        ]

    def save(self, *args, **kwargs):
        self.filters_json = normalize_feedback_filters(self.filters_json)
        self.filters_signature = build_feedback_signature(
            self.strain_id,
            self.filters_json,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} · {self.strain} · {self.feedback}"