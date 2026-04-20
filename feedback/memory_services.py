from collections import Counter

from .models import StrainFeedback

from decimal import Decimal

MEMORY_EFFECT_BOOST = Decimal("0.15")
MEMORY_TERPENE_BOOST = Decimal("0.12")
MEMORY_TYPE_BOOST = Decimal("0.08")



def build_user_memory_summary(user):
    summary = {
        "top_states": [],
        "top_effects": [],
        "top_terpenes": [],
        "top_strain_types": [],
        "saved_flow_count": 0,
        "recent_flow_count": 0,
        "liked_strain_count": 0,
    }

    if not user or not user.is_authenticated:
        return summary

    effect_counter = Counter()
    terpene_counter = Counter()
    type_counter = Counter()
    state_counter = Counter()

    liked_feedback = (
        StrainFeedback.objects
        .filter(user=user, feedback="like")
        .select_related("strain")
        .prefetch_related("strain__effects", "strain__terpenes")
    )

    summary["liked_strain_count"] = liked_feedback.count()

    for feedback in liked_feedback:
        strain = feedback.strain

        filters = feedback.filters_json or {}
        if filters.get("state"):
            state_counter[filters["state"]] += 1

        if strain.strain_type:
            type_counter[strain.strain_type] += 1

        for effect in strain.effects.all():
            effect_counter[effect.slug] += 1

        for terpene in strain.terpenes.all():
            terpene_counter[terpene.slug] += 1

    summary["top_states"] = [slug for slug, _ in state_counter.most_common(3)]
    summary["top_effects"] = [slug for slug, _ in effect_counter.most_common(3)]
    summary["top_terpenes"] = [slug for slug, _ in terpene_counter.most_common(3)]
    summary["top_strain_types"] = [slug for slug, _ in type_counter.most_common(2)]

    return summary

def get_memory_ranking_adjustment(strain, memory_summary):
    adjustment = Decimal("0.00")

    if not strain or not memory_summary:
        return adjustment

    top_effects = set(memory_summary.get("top_effects") or [])
    top_terpenes = set(memory_summary.get("top_terpenes") or [])
    top_types = set(memory_summary.get("top_strain_types") or [])

    for effect in strain.effects.all():
        if effect.slug in top_effects:
            adjustment += MEMORY_EFFECT_BOOST

    for terpene in strain.terpenes.all():
        if terpene.slug in top_terpenes:
            adjustment += MEMORY_TERPENE_BOOST

    if strain.strain_type and strain.strain_type in top_types:
        adjustment += MEMORY_TYPE_BOOST

    return adjustment