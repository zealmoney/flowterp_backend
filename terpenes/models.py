from django.db import models

from flowstate_labs.utils import generate_unique_slug


class Terpene(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    aroma_profile = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: citrus, earthy, pine"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Terpene"
        verbose_name_plural = "Terpenes"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)