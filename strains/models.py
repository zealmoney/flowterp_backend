from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from effects.models import Effect
from flowstate_labs.utils import generate_unique_slug
from states.models import CreativeState
from terpenes.models import Terpene


class StrainType(models.TextChoices):
    INDICA = "indica", "Indica"
    SATIVA = "sativa", "Sativa"
    HYBRID = "hybrid", "Hybrid"


class Strain(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    strain_type = models.CharField(
        max_length=20,
        choices=StrainType.choices,
        default=StrainType.HYBRID
    )

    description = models.TextField(blank=True)
    flavor_profile = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: sweet, creamy, vanilla, earthy"
    )
    aroma_profile = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: citrus, diesel, pine, floral"
    )

    thc_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    thc_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cbd_min = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    cbd_max = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    breeder = models.CharField(max_length=150, blank=True)
    lineage = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: Blueberry x Haze"
    )

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    terpenes = models.ManyToManyField(
        Terpene,
        through="StrainTerpene",
        related_name="strains",
        blank=True
    )
    effects = models.ManyToManyField(
        Effect,
        through="StrainEffect",
        related_name="strains",
        blank=True
    )
    states = models.ManyToManyField(
        CreativeState,
        through="StrainState",
        related_name="strains",
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Strain"
        verbose_name_plural = "Strains"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)


class StrainEffect(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="strain_effect_links"
    )
    effect = models.ForeignKey(
        Effect,
        on_delete=models.CASCADE,
        related_name="effect_strain_links"
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.50,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("strain", "effect")
        ordering = ["-score", "effect__name"]
        verbose_name = "Strain Effect"
        verbose_name_plural = "Strain Effects"

    def __str__(self) -> str:
        return f"{self.strain.name} → {self.effect.name} ({self.score})"


class StrainTerpene(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="strain_terpene_links"
    )
    terpene = models.ForeignKey(
        Terpene,
        on_delete=models.CASCADE,
        related_name="terpene_strain_links"
    )
    prominence = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.50,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("strain", "terpene")
        ordering = ["-prominence", "terpene__name"]
        verbose_name = "Strain Terpene"
        verbose_name_plural = "Strain Terpenes"

    def __str__(self) -> str:
        return f"{self.strain.name} → {self.terpene.name} ({self.prominence})"


class StrainState(models.Model):
    strain = models.ForeignKey(
        Strain,
        on_delete=models.CASCADE,
        related_name="strain_state_links"
    )
    state = models.ForeignKey(
        CreativeState,
        on_delete=models.CASCADE,
        related_name="state_strain_links"
    )
    score = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=0.50,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    best_time_of_day = models.CharField(
        max_length=100,
        blank=True,
        help_text="Example: morning, afternoon, late-night"
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ("strain", "state")
        ordering = ["-score", "state__name"]
        verbose_name = "Strain State"
        verbose_name_plural = "Strain States"

    def __str__(self) -> str:
        return f"{self.strain.name} → {self.state.name} ({self.score})"