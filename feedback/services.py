from decimal import Decimal

from .models import StrainFeedback, normalize_feedback_filters

from collections import defaultdict

LIKE_BOOST = Decimal("0.75")
DISLIKE_PENALTY = Decimal("1.00")


def build_feedback_lookup_with_fallback(user, filters):
    if not user or not user.is_authenticated:
        return {}

    normalized = normalize_feedback_filters(filters)

    # 🎯 1. Contextual feedback (exact match)
    contextual_qs = StrainFeedback.objects.filter(
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

    # 🌍 2. Global fallback feedback
    global_qs = StrainFeedback.objects.filter(
        user=user,
        filters_json__state="global",
        filters_json__mode="global",
    ).only("strain_id", "feedback")

    contextual_lookup = {
        item.strain_id: item.feedback
        for item in contextual_qs
    }

    global_lookup = {
        item.strain_id: item.feedback
        for item in global_qs
    }

    # 🧠 Merge with priority
    combined = {}

    for strain_id, feedback in global_lookup.items():
        combined[strain_id] = {
            "feedback": feedback,
            "source": "global",
        }

    for strain_id, feedback in contextual_lookup.items():
        combined[strain_id] = {
            "feedback": feedback,
            "source": "contextual",
        }

    return combined


def get_feedback_score_adjustment(strain_id, feedback_lookup, confidence):
    data = feedback_lookup.get(strain_id)

    if not data:
        return Decimal("0.00")

    feedback = data["feedback"]
    source = data["source"]

    base = Decimal("0.00")

    # Contextual (stronger)
    if source == "contextual":
        if feedback == "like":
            base = Decimal("1.00")
        elif feedback == "dislike":
            base = Decimal("-1.25")

    # Global (weaker)
    elif source == "global":
        if feedback == "like":
            base = Decimal("0.40")
        elif feedback == "dislike":
            base = Decimal("-0.60")

    return base * confidence


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


def compute_feedback_confidence(user):
    if not user or not user.is_authenticated:
        return Decimal("0.00")

    total_feedback = StrainFeedback.objects.filter(user=user).count()

    # 🎯 scale curve (tuneable)
    if total_feedback < 5:
        return Decimal("0.4")   # low confidence
    elif total_feedback < 15:
        return Decimal("0.7")
    elif total_feedback < 40:
        return Decimal("1.0")
    else:
        return Decimal("1.3")   # strong confidence



PER_STATE_EFFECT_BOOST = Decimal("0.18")
PER_STATE_TERPENE_BOOST = Decimal("0.14")
PER_STATE_TYPE_BOOST = Decimal("0.08")


def build_user_state_preference_profile(user, state_slug):
    profile = {
        "liked_effects": defaultdict(int),
        "disliked_effects": defaultdict(int),
        "liked_terpenes": defaultdict(int),
        "disliked_terpenes": defaultdict(int),
        "liked_strain_types": defaultdict(int),
        "disliked_strain_types": defaultdict(int),
        "feedback_count": 0,
    }

    if not user or not user.is_authenticated or not state_slug:
        return profile

    feedback_qs = (
        StrainFeedback.objects
        .filter(user=user, filters_json__state=state_slug)
        .select_related("strain")
        .prefetch_related("strain__effects", "strain__terpenes")
    )

    profile["feedback_count"] = feedback_qs.count()

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

def get_per_state_adjustment(strain, state_profile):
    adjustment = Decimal("0.00")

    if not strain or not state_profile:
        return adjustment

    # Do not over-trust per-state intelligence until there is enough data.
    if state_profile.get("feedback_count", 0) < 3:
        return adjustment

    for effect in strain.effects.all():
        liked = state_profile["liked_effects"].get(effect.slug, 0)
        disliked = state_profile["disliked_effects"].get(effect.slug, 0)

        if liked > disliked and liked > 0:
            adjustment += PER_STATE_EFFECT_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= PER_STATE_EFFECT_BOOST

    for terpene in strain.terpenes.all():
        liked = state_profile["liked_terpenes"].get(terpene.slug, 0)
        disliked = state_profile["disliked_terpenes"].get(terpene.slug, 0)

        if liked > disliked and liked > 0:
            adjustment += PER_STATE_TERPENE_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= PER_STATE_TERPENE_BOOST

    strain_type = strain.strain_type
    if strain_type:
        liked = state_profile["liked_strain_types"].get(strain_type, 0)
        disliked = state_profile["disliked_strain_types"].get(strain_type, 0)

        if liked > disliked and liked > 0:
            adjustment += PER_STATE_TYPE_BOOST
        elif disliked > liked and disliked > 0:
            adjustment -= PER_STATE_TYPE_BOOST

    return adjustment