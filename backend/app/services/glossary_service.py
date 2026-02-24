"""Bilingual glossary service for Temporal Cartography surfaces."""

from __future__ import annotations

from datetime import datetime, timezone

from .runtime_cache import cached

SUPPORTED_DOMAINS = {"panchanga", "muhurta", "kundali"}
SUPPORTED_LANGS = {"en", "ne"}


GLOSSARY_DATA = {
    "en": {
        "panchanga": {
            "title": "Panchanga Basics",
            "intro": "Panchanga describes the day through five astronomical markers used in ritual timing.",
            "sections": [
                {
                    "id": "five-limbs",
                    "title": "Five Limbs",
                    "terms": [
                        {"name": "Tithi", "meaning": "Lunar day from Moon-Sun angular distance.", "why_it_matters": "Most observances are tied to a tithi at sunrise."},
                        {"name": "Nakshatra", "meaning": "The Moon's current star sector among 27.", "why_it_matters": "Used for naming, rituals, and muhurta filters."},
                        {"name": "Yoga", "meaning": "Sun-Moon combined angular classification.", "why_it_matters": "Traditionally used as a day quality indicator."},
                        {"name": "Karana", "meaning": "Half-tithi subdivision for finer time windows.", "why_it_matters": "Helps select narrower action intervals."},
                        {"name": "Vaara", "meaning": "Weekday cycle (Ravivara, Somavara, ...).", "why_it_matters": "Weekday-specific rules affect observance planning."},
                    ],
                },
            ],
        },
        "muhurta": {
            "title": "Muhurta Interpretation Guide",
            "intro": "Muhurta ranks time windows for specific ceremony goals using rule profiles.",
            "sections": [
                {
                    "id": "core",
                    "title": "Core Terms",
                    "terms": [
                        {"name": "Muhurta", "meaning": "A ritual time segment used for planning.", "why_it_matters": "Windows are ranked, not all treated equal."},
                        {"name": "Rahu Kalam", "meaning": "A weekday-based avoid window.", "why_it_matters": "Commonly avoided for new beginnings."},
                        {"name": "Hora", "meaning": "Planetary hour sequence through day/night.", "why_it_matters": "Adds context-specific weighting to windows."},
                        {"name": "Chaughadia", "meaning": "Day/night slot quality cycle.", "why_it_matters": "Adds a second layer of favorable/unfavorable signals."},
                        {"name": "Tara Bala", "meaning": "Birth-star compatibility indicator.", "why_it_matters": "Personalizes rankings when birth nakshatra is known."},
                    ],
                },
            ],
        },
        "kundali": {
            "title": "Kundali Reading Primer",
            "intro": "Kundali maps graha positions at birth time and location into a structured chart.",
            "sections": [
                {
                    "id": "building-blocks",
                    "title": "Building Blocks",
                    "terms": [
                        {"name": "Lagna", "meaning": "Rising sign at birth moment.", "why_it_matters": "Defines house framework for the chart."},
                        {"name": "Graha", "meaning": "Nine key Vedic planetary points.", "why_it_matters": "Positions and relations drive interpretations."},
                        {"name": "House", "meaning": "One of 12 life domains in the chart.", "why_it_matters": "Shows where influences manifest."},
                        {"name": "Dasha", "meaning": "Planetary period timeline.", "why_it_matters": "Used for time-phase interpretation."},
                        {"name": "Yoga / Dosha", "meaning": "Pattern markers from planetary combinations.", "why_it_matters": "Highlights notable strengths and caution zones."},
                    ],
                },
            ],
        },
    },
    "ne": {
        "panchanga": {
            "title": "पञ्चाङ्ग के हो?",
            "intro": "पञ्चाङ्गले दिनलाई पाँच खगोलीय आधारबाट व्याख्या गर्छ, जसले पूजा/व्रतको समय निर्धारणमा मद्दत गर्छ।",
            "sections": [
                {
                    "id": "five-limbs",
                    "title": "पाँच अङ्ग",
                    "terms": [
                        {"name": "तिथि", "meaning": "चन्द्र–सूर्य कोणीय दूरीबाट निस्कने चन्द्रदिन।", "why_it_matters": "धेरै व्रत/पर्व सूर्योदयको तिथिमा आधारित हुन्छन्।"},
                        {"name": "नक्षत्र", "meaning": "चन्द्रमा रहेको नक्षत्र खण्ड (२७ मध्ये)।", "why_it_matters": "मूहुर्त, नामकरण र धार्मिक कार्यमा प्रयोग हुन्छ।"},
                        {"name": "योग", "meaning": "सूर्य–चन्द्र समायोजनबाट बनिने योग।", "why_it_matters": "दिनको समग्र गुण बुझ्न प्रयोग हुन्छ।"},
                        {"name": "करण", "meaning": "तिथिको आधा भाग।", "why_it_matters": "दिनभित्रका सूक्ष्म समय खण्ड छान्न उपयोगी।"},
                        {"name": "वार", "meaning": "साप्ताहिक दिन (रवि, सोम, आदि)।", "why_it_matters": "कर्म/विधि अनुसार दिनको नियम फरक हुन्छ।"},
                    ],
                }
            ],
        },
        "muhurta": {
            "title": "मूहुर्त बुझ्ने तरिका",
            "intro": "मूहुर्तले कार्यको लागि उपयुक्त समय खण्ड देखाउँछ। Parva ले नियमअनुसार समयलाई क्रमबद्ध गर्छ।",
            "sections": [
                {
                    "id": "core",
                    "title": "मुख्य शब्दहरू",
                    "terms": [
                        {"name": "मूहुर्त", "meaning": "धार्मिक/शुभ कार्यको समय खण्ड।", "why_it_matters": "सबै समय बराबर मानिँदैन, गुणस्तर फरक हुन्छ।"},
                        {"name": "राहु काल", "meaning": "बार अनुसार टारिने समय।", "why_it_matters": "नयाँ काम सुरु गर्दा प्रायः टारिन्छ।"},
                        {"name": "होरा", "meaning": "दिन/रातका ग्रहघण्टा क्रम।", "why_it_matters": "कार्यअनुसार उपयुक्तता बढ्छ वा घट्छ।"},
                        {"name": "चौघडिया", "meaning": "दिन/रातका ८ गुण वर्ग।", "why_it_matters": "शुभ/अशुभ संकेत थप स्पष्ट हुन्छ।"},
                        {"name": "ताराबल", "meaning": "जन्म नक्षत्र र आजको नक्षत्रको मिलान।", "why_it_matters": "व्यक्तिगत सिफारिस अझ सटीक हुन्छ।"},
                    ],
                }
            ],
        },
        "kundali": {
            "title": "कुण्डली आधारभूत मार्गदर्शिका",
            "intro": "कुण्डलीले जन्म समय र स्थानका आधारमा ग्रहस्थिति देखाएर व्याख्या गर्न मद्दत गर्छ।",
            "sections": [
                {
                    "id": "building-blocks",
                    "title": "मुख्य आधार",
                    "terms": [
                        {"name": "लग्न", "meaning": "जन्म समयमा पूर्व क्षितिजमा उदाएको राशि।", "why_it_matters": "घरहरूको प्रारम्भ र चार्टको आधार बन्छ।"},
                        {"name": "ग्रह", "meaning": "नवग्रह सम्बन्धित बिन्दुहरू।", "why_it_matters": "ग्रहस्थिति र सम्बन्धबाट अर्थ निक्लन्छ।"},
                        {"name": "भाव", "meaning": "१२ जीवन-क्षेत्रहरू।", "why_it_matters": "कुन क्षेत्रमा प्रभाव पर्छ भनेर देखाउँछ।"},
                        {"name": "दशा", "meaning": "ग्रहकालको समयरेखा।", "why_it_matters": "समयसापेक्ष व्याख्यामा उपयोगी।"},
                        {"name": "योग/दोष", "meaning": "ग्रह संयोजनबाट बनेका संकेत।", "why_it_matters": "बलियो पक्ष र सावधानीका क्षेत्र देखाउँछ।"},
                    ],
                }
            ],
        },
    },
}


def get_glossary(*, domain: str, lang: str) -> dict:
    domain_key = (domain or "").strip().lower()
    lang_key = (lang or "").strip().lower()

    if domain_key not in SUPPORTED_DOMAINS:
        raise ValueError(f"Unsupported glossary domain '{domain}'.")

    if lang_key not in SUPPORTED_LANGS:
        lang_key = "en"

    cache_key = f"glossary:{domain_key}:{lang_key}"

    def _compute() -> dict:
        payload = GLOSSARY_DATA[lang_key][domain_key]
        return {
            "domain": domain_key,
            "lang": lang_key,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "content": payload,
        }

    return cached(cache_key, ttl_seconds=3600, compute=_compute)
