"""
Mythology Repository
====================

Data access layer for deity and mythology content.
"""

from __future__ import annotations

from typing import Dict, List, Optional
from functools import lru_cache

from .models import Deity, DeitySummary


# Built-in deity data for core festivals
DEITIES: Dict[str, Deity] = {
    "durga": Deity(
        id="durga",
        name="Durga",
        name_nepali="दुर्गा",
        name_sanskrit="दुर्गा",
        role="Goddess of power, war, and protection",
        domain=["protection", "power", "victory", "motherhood"],
        iconography="Multi-armed goddess riding a lion/tiger, holding weapons",
        vahana="Lion (Simha) or Tiger",
        consort="Shiva",
        mythology="Durga is the warrior goddess created by the combined powers of all gods to defeat the buffalo demon Mahishasura. Her nine forms (Navadurga) are worshipped during Dashain.",
        nepali_significance="Central deity of Dashain, Nepal's largest festival. The nine nights of Navaratri honor her nine forms.",
        associated_festivals=["dashain"],
        associated_temples=[]
    ),
    "lakshmi": Deity(
        id="lakshmi",
        name="Lakshmi",
        name_nepali="लक्ष्मी",
        name_sanskrit="लक्ष्मी",
        role="Goddess of wealth, fortune, and prosperity",
        domain=["wealth", "prosperity", "fortune", "beauty"],
        iconography="Four-armed goddess seated on lotus, holding lotus flowers, gold coins flowing",
        vahana="Owl (Uluka)",
        consort="Vishnu",
        mythology="Lakshmi emerged from the churning of the ocean (Samudra Manthan) and chose Vishnu as her eternal consort. She brings prosperity wherever she is welcomed.",
        nepali_significance="Worshipped on Laxmi Puja during Tihar. Houses are cleaned and lit with oil lamps to welcome her.",
        associated_festivals=["tihar"],
        associated_temples=[]
    ),
    "indra": Deity(
        id="indra",
        name="Indra",
        name_nepali="इन्द्र",
        name_sanskrit="इन्द्र",
        role="King of gods, god of rain, thunder, and storms",
        domain=["rain", "storms", "thunder", "heaven", "war"],
        iconography="Rides white elephant Airavata, holds thunderbolt (vajra)",
        vahana="Airavata (white elephant)",
        consort="Shachi (Indrani)",
        mythology="Indra rules Svarga (heaven) and controls weather. In the legend of Indra Jatra, he descended to steal parijat flowers and was captured by the valley's residents.",
        nepali_significance="Indra Jatra celebrates his capture and release, bringing the blessing of rain for harvest.",
        associated_festivals=["indra-jatra"],
        associated_temples=[]
    ),
    "kumari": Deity(
        id="kumari",
        name="Kumari",
        name_nepali="कुमारी",
        name_sanskrit="कुमारी",
        role="Living goddess, manifestation of Taleju/Durga",
        domain=["divine feminine", "protection", "blessing"],
        iconography="Young girl with third eye painted on forehead, elaborate traditional dress",
        vahana=None,
        consort=None,
        mythology="The Kumari is a living goddess worshipped by both Hindus and Buddhists. Selected as young girls from the Shakya caste, they embody the goddess Taleju until puberty.",
        nepali_significance="The Royal Kumari of Kathmandu appears during Indra Jatra and blesses the nation. Three Kumaris exist in the valley.",
        associated_festivals=["indra-jatra", "dashain"],
        associated_temples=[]
    ),
    "shiva": Deity(
        id="shiva",
        name="Shiva",
        name_nepali="शिव",
        name_sanskrit="शिव",
        role="The Destroyer, god of transformation and meditation",
        domain=["destruction", "transformation", "meditation", "dance", "yoga"],
        iconography="Third eye, crescent moon, trident, matted hair, snake around neck",
        vahana="Nandi (bull)",
        consort="Parvati",
        mythology="Shiva is the third member of the Hindu trinity. He destroys to enable recreation. Pashupatinath is one of his most sacred temples.",
        nepali_significance="Pashupatinath Temple is the holiest Shiva temple. Shivaratri brings hundreds of thousands of devotees and sadhus.",
        associated_festivals=["shivaratri"],
        associated_temples=[]
    ),
    "krishna": Deity(
        id="krishna",
        name="Krishna",
        name_nepali="कृष्ण",
        name_sanskrit="कृष्ण",
        role="Avatar of Vishnu, god of love and compassion",
        domain=["love", "compassion", "music", "divine play"],
        iconography="Blue-skinned, playing flute, wearing peacock feather crown",
        vahana="Garuda (through Vishnu)",
        consort="Radha, Rukmini",
        mythology="Krishna is the eighth avatar of Vishnu. His life story from mischievous child to divine warrior is central to Hindu philosophy through the Bhagavad Gita.",
        nepali_significance="Krishna Mandir in Patan is a major pilgrimage site. Krishna Janmashtami celebrates his birth with midnight celebrations.",
        associated_festivals=["holi", "krishna-janmashtami"],
        associated_temples=[]
    ),
    "buddha": Deity(
        id="buddha",
        name="Buddha",
        name_nepali="बुद्ध",
        name_sanskrit="बुद्ध",
        role="The Enlightened One, founder of Buddhism",
        domain=["enlightenment", "wisdom", "compassion", "liberation"],
        iconography="Seated in meditation pose, elongated earlobes, ushnisha (crown protrusion)",
        vahana=None,
        consort=None,
        mythology="Siddhartha Gautama was born in Lumbini, Nepal, and attained enlightenment to become the Buddha. His teachings form the foundation of Buddhism.",
        nepali_significance="Nepal is Buddha's birthplace. Lumbini, Swayambhunath, and Boudhanath are major Buddhist sites.",
        associated_festivals=["buddha-jayanti"],
        associated_temples=[]
    ),
    "bhairav": Deity(
        id="bhairav",
        name="Bhairav",
        name_nepali="भैरव",
        name_sanskrit="भैरव",
        role="Fierce manifestation of Shiva, guardian deity",
        domain=["protection", "destruction of evil", "time", "death"],
        iconography="Fierce expression, multiple arms, skull garland, weapons, black or red color",
        vahana="Dog",
        consort="Bhairavi",
        mythology="Bhairav is the wrathful form of Shiva. He guards sacred spaces and destroys evil. Various forms include Kal Bhairav and Akash Bhairav.",
        nepali_significance="Prominent in Newari culture. Akash Bhairav's mask is displayed during Indra Jatra. Kal Bhairav statue at Durbar Square is famous.",
        associated_festivals=["indra-jatra", "bisket-jatra"],
        associated_temples=[]
    ),
}


@lru_cache(maxsize=1)
def _get_all_deities() -> Dict[str, Deity]:
    """Get all deities (cached)."""
    return DEITIES.copy()


def get_deity(deity_id: str) -> Optional[Deity]:
    """
    Get a deity by ID.
    
    Args:
        deity_id: The deity identifier
        
    Returns:
        Deity if found, None otherwise
    """
    return DEITIES.get(deity_id)


def get_all_deities() -> List[DeitySummary]:
    """
    Get all deities as summaries.
    
    Returns:
        List of deity summaries
    """
    return [
        DeitySummary(
            id=d.id,
            name=d.name,
            name_nepali=d.name_nepali,
            role=d.role,
            associated_festivals=d.associated_festivals
        )
        for d in DEITIES.values()
    ]


def get_deity_festivals(deity_id: str) -> List[str]:
    """
    Get festivals associated with a deity.
    
    Args:
        deity_id: The deity identifier
        
    Returns:
        List of festival IDs
    """
    deity = get_deity(deity_id)
    if deity:
        return deity.associated_festivals
    return []


def get_deities_for_festival(festival_id: str) -> List[DeitySummary]:
    """
    Get deities associated with a festival.
    
    Args:
        festival_id: The festival identifier
        
    Returns:
        List of deity summaries
    """
    return [
        DeitySummary(
            id=d.id,
            name=d.name,
            name_nepali=d.name_nepali,
            role=d.role,
            associated_festivals=d.associated_festivals
        )
        for d in DEITIES.values()
        if festival_id in d.associated_festivals
    ]
