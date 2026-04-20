from decimal import Decimal

from .models import StrainFeedback, normalize_feedback_filters

from collections import defaultdict


LIKE_BOOST = Decimal("0.75")
DISLIKE_PENALTY = Decimal("1.00")


def build_feedback_lookup_for_user(user, filters):
    """
    Returns a dict keyed by strain_id for feedback matching the current normalized filter context.
    """
    if not user or not user.is_authenticated:
        return {}

    normalized = normalize_feedback_filters(filters)

    feedback_qs = StrainFeedback.objects.filter(
        user=user,
        filters_json__state=normalized["state"],
        filters_json__effect=normalized["effect"],
        filters_json__terpene=normalized["terpene"],
        filters_json__time_of_day=normalized["time_of_day"],
        filters_json__strain_type=normalized["strain_type"],
        filters_json__featured=normalized["featured"],
        filters_json__min_thc=normalized["min_thc"],
        filters_json__max_thc=normalized["max_thc"],
        filters_json__mode=normalized["mode"],
    ).only("strain_id", "feedback")

    return {
        item.strain_id: item.feedback
        for item in feedback_qs
    }


def get_feedback_score_adjustment(strain_id, feedback_lookup):
    """
    Returns a Decimal score adjustment for a given strain based on saved feedback.
    """
    feedback_value = feedback_lookup.get(strain_id)

    if feedback_value == "like":
        return LIKE_BOOST

    if feedback_value == "dislike":
        return -DISLIKE_PENALTY

    return Decimal("0.00")


EFFECT_LIKE_BOOST = Decimal("0.20")
EFFECT_DISLIKE_PENALTY = Decimal("0.25")
TERPENE_LIKE_BOOST = Decimal("0.15")
TERPENE_DISLIKE_PENALTY = Decimal("0.20")
TYPE_LIKE_BOOST = Decimal("0.10")
TYPE_DISLIKE_PENALTY = Decimal("0.10")


def build_user_preference_profile(user):
    profile = {
        "liked_effects": defaultdict(int),
        "disliked_effects": defaultdict(int),
        "liked_terpenes": defaultdict(int),
        "disliked_terpenes": defaultdict(int),
        "liked_strain_types": defaultdict(int),
        "disliked_strain_types": defaultdict(int),
    }

    if not user or not user.is_authenticated:
        return profile

    feedback_qs = (
        StrainFeedback.objects
        .filter(user=user)
        .select_related("strain")
        .prefetch_related("strain__effects", "strain__terpenes")
    )

    for feedback in feedback_qs:
        strain = feedback.strain
        bucket = "liked" if feedback.feedback == "like" else "disliked"

        for effect in strain.effects.all():
            profile[f"{bucket}_effects"][effect.slug] += 1

        for terpene in strain.terpenes.all():
            profile[f"{bucket}_terpenes"][terpene.slug] += 1

        if strain.strain_type:
            profile[f"{bucket}_strain_types"][strain.strain_type] += 1

    return profile


def get_personalization_adjustment(strain, profile):
    adjustment = Decimal("0.00")

    for effect in strain.effects.all():
        liked = profile["liked_effects"].get(effect.slug, 0)
        disliked = profile["disliked_effects"].get(effect.slug, 0)

        if liked > disliked and liked > 0:
            adjustment += EFFECT_LIKE_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= EFFECT_DISLIKE_PENALTY

    for terpene in strain.terpenes.all():
        liked = profile["liked_terpenes"].get(terpene.slug, 0)
        disliked = profile["disliked_terpenes"].get(terpene.slug, 0)

        if liked > disliked and liked > 0:
            adjustment += TERPENE_LIKE_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= TERPENE_DISLIKE_PENALTY

    strain_type = strain.strain_type
    if strain_type:
        liked = profile["liked_strain_types"].get(strain_type, 0)
        disliked = profile["disliked_strain_types"].get(strain_type, 0)

        if liked > disliked and liked > 0:
            adjustment += TYPE_LIKE_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= TYPE_DISLIKE_PENALTY

    return adjustment