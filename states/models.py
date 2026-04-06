from django.db import models

from flowstate_labs.utils import generate_unique_slug


class CreativeState(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    intended_use = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: video editing, coding, music production, writing"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Creative State"
        verbose_name_plural = "Creative States"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)