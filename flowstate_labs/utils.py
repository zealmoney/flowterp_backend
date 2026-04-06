from django.utils.text import slugify


def generate_unique_slug(instance, value, slug_field_name="slug"):
    """
    Generate a unique slug for a model instance.
    """
    slug = slugify(value)
    model_class = instance.__class__

    if not slug:
        slug = "item"

    unique_slug = slug
    counter = 1

    while model_class.objects.filter(**{slug_field_name: unique_slug}).exclude(pk=instance.pk).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    return unique_slug