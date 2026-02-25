"""
Festival Data Repository
========================

Handles loading, caching, and querying festival data from JSON files.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from typing import Optional, List, Dict, Any
from functools import lru_cache

from .models import (
    Festival,
    FestivalSummary,
    UpcomingFestival,
    FestivalDates,
)
from ..calendar import (
    gregorian_to_bs,
    get_bs_month_name,
    calculate_tithi,
)
from ..rules import get_rule_service


# Path to festival data files
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "festivals"


def _to_bs_struct(g_date: date) -> dict:
    bs_year, bs_month, bs_day = gregorian_to_bs(g_date)
    month_name = get_bs_month_name(bs_month)
    return {
        "year": bs_year,
        "month": bs_month,
        "day": bs_day,
        "month_name": month_name,
        "formatted": f"{bs_year} {month_name} {bs_day}",
    }


class FestivalRepository:
    """
    Repository for festival data access.
    
    Loads festivals from JSON and provides query methods.
    Caches data in memory for performance.
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize repository.
        
        Args:
            data_dir: Path to data directory (defaults to data/festivals/)
        """
        self.data_dir = data_dir or DATA_DIR
        self._festivals: Dict[str, Festival] = {}
        self._loaded = False
        self._rule_service = get_rule_service()
    
    def _ensure_loaded(self) -> None:
        """Ensure festival data is loaded."""
        if not self._loaded:
            self._load_festivals()
    
    def _load_festivals(self) -> None:
        """Load all festival data from JSON file."""
        festivals_file = self.data_dir / "festivals.json"
        
        if not festivals_file.exists():
            # If no file exists, use built-in minimal data
            self._load_builtin_festivals()
            self._loaded = True
            return
        
        try:
            with open(festivals_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for festival_data in data.get("festivals", []):
                festival = Festival(**festival_data)
                self._festivals[festival.id] = festival
            
            self._loaded = True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Warning: Could not load festivals.json: {e}")
            self._load_builtin_festivals()
            self._loaded = True
    
    def _load_builtin_festivals(self) -> None:
        """Load minimal built-in festival data."""
        # Define minimal festival data for supported festivals
        builtin = [
            Festival(
                id="dashain",
                name="Dashain",
                name_nepali="दशैं",
                calendar_type="lunar",
                category="national",
                significance_level=5,
                tagline="Nepal's greatest festival celebrating victory of good over evil",
                description="Dashain is the longest and most auspicious Hindu festival in Nepal, "
                           "lasting for 15 days. It celebrates the victory of goddess Durga over "
                           "the demon Mahishasura, symbolizing the triumph of good over evil. "
                           "Families reunite, elders give blessings and tika, and there is an "
                           "atmosphere of joy and celebration throughout the country.",
                typical_month_bs=6,
                typical_month_gregorian="September-October",
                duration_days=15,
                is_national_holiday=True,
                primary_color="#9B1B30",
                content_status="basic"
            ),
            Festival(
                id="tihar",
                name="Tihar",
                name_nepali="तिहार",
                calendar_type="lunar",
                category="national", 
                significance_level=5,
                tagline="Festival of lights honoring crows, dogs, cows, oxen, and siblings",
                description="Tihar is Nepal's second-largest festival, also known as Deepawali. "
                           "Over five days, different animals are honored: crows (Kaag Tihar), "
                           "dogs (Kukur Tihar), and cows (Gai Tihar). The main days feature "
                           "Laxmi Puja with beautiful oil lamps and rangoli, followed by "
                           "Bhai Tika where sisters bless their brothers.",
                typical_month_bs=7,
                typical_month_gregorian="October-November",
                duration_days=5,
                is_national_holiday=True,
                primary_color="#FFD700",
                content_status="basic"
            ),
            Festival(
                id="holi",
                name="Holi",
                name_nepali="होली",
                calendar_type="lunar",
                category="national",
                significance_level=4,
                tagline="Festival of colors celebrating spring and love",
                description="Holi is the festival of colors, celebrated on the full moon of "
                           "Falgun. People throw colored powder and water at each other, dancing "
                           "and celebrating the arrival of spring. The day before, Holika Dahan "
                           "marks the burning of the demoness Holika, symbolizing victory over evil.",
                typical_month_bs=11,
                typical_month_gregorian="February-March",
                duration_days=2,
                is_national_holiday=True,
                primary_color="#FF6B6B",
                content_status="basic"
            ),
            Festival(
                id="indra-jatra",
                name="Indra Jatra",
                name_nepali="इन्द्र जात्रा",
                calendar_type="lunar",
                category="newari",
                significance_level=5,
                tagline="Kathmandu's grandest street festival with the Living Goddess",
                description="Indra Jatra is Kathmandu's most spectacular street festival, "
                           "lasting eight days in September. It honors the god Indra and features "
                           "the appearance of Kumari, the Living Goddess. The Lakhey demon dance, "
                           "chariot processions, and masked dances fill the old city. This festival "
                           "marks the end of monsoon and the beginning of the festival season.",
                typical_month_bs=5,
                typical_month_gregorian="August-September",
                duration_days=8,
                is_national_holiday=False,
                regional_focus=["Kathmandu Valley"],
                primary_color="#C41E3A",
                content_status="basic"
            ),
            Festival(
                id="teej",
                name="Teej",
                name_nepali="तीज",
                calendar_type="lunar",
                category="national",
                significance_level=4,
                tagline="Women's festival of fasting, dancing, and devotion",
                description="Teej is a three-day festival primarily celebrated by Hindu women. "
                           "They dress in red saris, sing traditional songs, and fast for the "
                           "well-being of their husbands. The festival honors goddess Parvati "
                           "and her devotion to Lord Shiva. Women gather at temples, especially "
                           "Pashupatinath, to perform rituals.",
                typical_month_bs=5,
                typical_month_gregorian="August-September",
                duration_days=3,
                is_national_holiday=True,
                primary_color="#DC143C",
                content_status="basic"
            ),
            Festival(
                id="shivaratri",
                name="Maha Shivaratri",
                name_nepali="महाशिवरात्री",
                calendar_type="lunar",
                category="national",
                significance_level=5,
                tagline="Night of Lord Shiva with all-night vigils at Pashupatinath",
                description="Maha Shivaratri is one of the most important Hindu festivals, "
                           "celebrated on the 14th day of the dark fortnight in Falgun. "
                           "Devotees fast and stay awake all night in honor of Lord Shiva. "
                           "Pashupatinath Temple becomes the center of celebrations, attracting "
                           "sadhus from across South Asia.",
                typical_month_bs=11,
                typical_month_gregorian="February-March",
                duration_days=1,
                is_national_holiday=True,
                primary_color="#1E3A5F",
                content_status="basic"
            ),
            Festival(
                id="buddha-jayanti",
                name="Buddha Jayanti",
                name_nepali="बुद्ध जयन्ती",
                calendar_type="lunar",
                category="buddhist",
                significance_level=4,
                tagline="Celebrating Buddha's birth, enlightenment, and passing",
                description="Buddha Jayanti marks the birth, enlightenment, and death of "
                           "Gautama Buddha. In Nepal, it's celebrated on the full moon of "
                           "Baisakh with processions, prayers, and visits to Buddhist sites. "
                           "Lumbini, Buddha's birthplace, and Swayambhunath in Kathmandu see "
                           "the largest gatherings.",
                typical_month_bs=2,
                typical_month_gregorian="April-May",
                duration_days=1,
                is_national_holiday=True,
                primary_color="#F4A460",
                content_status="basic"
            ),
            Festival(
                id="janai-purnima",
                name="Janai Purnima",
                name_nepali="जनैपूर्णिमा",
                calendar_type="lunar",
                category="national",
                significance_level=3,
                tagline="Sacred thread ceremony and Raksha Bandhan",
                description="Janai Purnima is the full moon day when Hindu men change their "
                           "sacred thread (janai). Everyone receives a sacred thread (raksha) "
                           "tied on their wrist for protection. It's also celebrated as "
                           "Raksha Bandhan in some communities, where sisters tie threads "
                           "on their brothers' wrists.",
                typical_month_bs=4,
                typical_month_gregorian="July-August",
                duration_days=1,
                is_national_holiday=True,
                primary_color="#FFD700",
                content_status="basic"
            ),
            Festival(
                id="gai-jatra",
                name="Gai Jatra",
                name_nepali="गाईजात्रा",
                calendar_type="lunar",
                category="newari",
                significance_level=4,
                tagline="Festival of cows honoring the deceased with humor and satire",
                description="Gai Jatra is a unique Newari festival where families who lost "
                           "members in the past year lead cows through the streets, believing "
                           "cows help guide souls to heaven. Over time, it evolved into a "
                           "carnival of satire and comedy, with people mocking politicians "
                           "and social issues.",
                typical_month_bs=4,
                typical_month_gregorian="August",
                duration_days=1,
                is_national_holiday=False,
                regional_focus=["Kathmandu Valley"],
                primary_color="#2E8B57",
                content_status="basic"
            ),
            Festival(
                id="mha-puja",
                name="Mha Puja",
                name_nepali="म्ह पूजा",
                calendar_type="lunar",
                category="newari",
                significance_level=4,
                tagline="Worship of self and Nepal Sambat New Year",
                description="Mha Puja falls on the fourth day of Tihar and is unique to the "
                           "Newari community. It marks Nepal Sambat New Year and involves "
                           "worshipping oneself, acknowledging one's life force. Elaborate "
                           "mandalas are created, and the ritual celebrates the divine within.",
                typical_month_bs=7,
                typical_month_gregorian="October-November",
                duration_days=1,
                is_national_holiday=False,
                regional_focus=["Kathmandu Valley"],
                primary_color="#FF6347",
                content_status="basic"
            ),
            Festival(
                id="yomari-punhi",
                name="Yomari Punhi",
                name_nepali="योमरी पुन्ही",
                calendar_type="lunar",
                category="newari",
                significance_level=3,
                tagline="Newari harvest festival with sweet rice dumplings",
                description="Yomari Punhi is a Newari festival celebrating the rice harvest. "
                           "Families make yomari, crescent-shaped rice flour dumplings filled "
                           "with chaku (sweet molasses). It's celebrated on the full moon of "
                           "Poush and is associated with joy and plenty after a good harvest.",
                typical_month_bs=9,
                typical_month_gregorian="December",
                duration_days=1,
                is_national_holiday=False,
                regional_focus=["Kathmandu Valley"],
                primary_color="#8B4513",
                content_status="basic"
            ),
            Festival(
                id="maghe-sankranti",
                name="Maghe Sankranti",
                name_nepali="माघे संक्रान्ति",
                calendar_type="solar",
                category="national",
                significance_level=3,
                tagline="Winter solstice celebration with special foods and holy baths",
                description="Maghe Sankranti marks the transition of the sun into Capricorn "
                           "and the first day of the month of Magh. It's celebrated with "
                           "special foods like til ko laddu (sesame sweets), yam, and ghee. "
                           "People take holy dips in rivers, especially at Devghat.",
                typical_month_bs=10,
                typical_month_gregorian="January",
                duration_days=1,
                is_national_holiday=True,
                primary_color="#4169E1",
                content_status="basic"
            ),
            Festival(
                id="bs-new-year",
                name="Nepali New Year",
                name_nepali="नयाँ वर्ष",
                calendar_type="solar",
                category="national",
                significance_level=4,
                tagline="Beginning of the Bikram Sambat calendar year",
                description="Nepali New Year (Naya Barsha) falls on Baishakh 1 and marks the "
                           "beginning of the Bikram Sambat calendar. It's celebrated with "
                           "family gatherings, special foods, and cultural programs. The day "
                           "is a national holiday, and people visit temples and exchange greetings.",
                typical_month_bs=1,
                typical_month_gregorian="April",
                duration_days=1,
                is_national_holiday=True,
                primary_color="#228B22",
                content_status="basic"
            ),
            Festival(
                id="bisket-jatra",
                name="Bisket Jatra",
                name_nepali="बिस्केट जात्रा",
                calendar_type="solar",
                category="newari",
                significance_level=4,
                tagline="Bhaktapur's dramatic New Year chariot festival",
                description="Bisket Jatra is Bhaktapur's spectacular New Year celebration. "
                           "Massive chariots of Bhairab are pulled through the streets, and "
                           "a giant lingam pole is erected. On New Year's Day, the pole is "
                           "toppled, marking the new year. It's one of Nepal's most dramatic "
                           "and ancient festivals.",
                typical_month_bs=12,
                typical_month_gregorian="April",
                duration_days=9,
                is_national_holiday=False,
                regional_focus=["Bhaktapur"],
                primary_color="#8B0000",
                content_status="basic"
            ),
            Festival(
                id="ghode-jatra",
                name="Ghode Jatra",
                name_nepali="घोडे जात्रा",
                calendar_type="lunar",
                category="newari",
                significance_level=3,
                tagline="Horse parade festival at Tundikhel",
                description="Ghode Jatra is a unique horse parade festival held at Tundikhel "
                           "in Kathmandu. According to legend, the thundering hooves keep "
                           "evil spirits underground. The Nepal Army performs spectacular "
                           "horse acrobatics, and it's one of Kathmandu's most popular festivals.",
                typical_month_bs=12,
                typical_month_gregorian="March-April",
                duration_days=1,
                is_national_holiday=False,
                regional_focus=["Kathmandu"],
                primary_color="#8B4513",
                content_status="basic"
            ),
            Festival(
                id="rato-machhindranath",
                name="Rato Machhindranath Jatra",
                name_nepali="रातो मच्छिन्द्रनाथ जात्रा",
                calendar_type="lunar",
                category="newari",
                significance_level=5,
                tagline="Nepal's longest chariot festival in Patan",
                description="Rato Machhindranath Jatra in Patan is Nepal's longest festival, "
                           "with the chariot procession lasting about a month. The deity is "
                           "revered by both Hindus (as Avalokiteshvara) and Buddhists "
                           "(as Machhindranath). The bhoto jatra, showing the sacred vest, "
                           "traditionally occurs in the presence of the King.",
                typical_month_bs=1,
                typical_month_gregorian="April-May",
                duration_days=30,
                is_national_holiday=False,
                regional_focus=["Patan", "Bungamati"],
                primary_color="#DC143C",
                content_status="basic"
            ),
        ]
        
        for festival in builtin:
            self._festivals[festival.id] = festival
    
    def get_all(self) -> List[Festival]:
        """Get all festivals."""
        self._ensure_loaded()
        return list(self._festivals.values())
    
    def get_by_id(self, festival_id: str) -> Optional[Festival]:
        """Get a festival by ID."""
        self._ensure_loaded()
        return self._festivals.get(festival_id)
    
    def get_by_category(self, category: str) -> List[Festival]:
        """Get festivals by category."""
        self._ensure_loaded()
        return [f for f in self._festivals.values() if f.category == category]
    
    def get_by_month(self, bs_month: int) -> List[Festival]:
        """Get festivals by BS month."""
        self._ensure_loaded()
        return [
            f for f in self._festivals.values()
            if f.typical_month_bs == bs_month
        ]
    
    def search(self, query: str) -> List[Festival]:
        """Search festivals by name or description."""
        self._ensure_loaded()
        query = query.lower()
        return [
            f for f in self._festivals.values()
            if query in f.name.lower() 
            or query in (f.name_nepali or "").lower()
            or query in f.description.lower()
            or query in f.tagline.lower()
        ]
    
    def get_dates(self, festival_id: str, year: int) -> Optional[FestivalDates]:
        """Get calculated dates for a festival in a specific year."""
        if festival_id not in self._rule_service.list_ids():
            return None
        
        try:
            result = self._rule_service.calculate(festival_id, year)
            if result is None:
                return None
            
            bs_start = _to_bs_struct(result.start_date)
            bs_end = _to_bs_struct(result.end_date)
            days_until = (result.start_date - date.today()).days

            return FestivalDates(
                gregorian_year=year,
                bs_year=bs_start["year"],
                start_date=result.start_date,
                end_date=result.end_date,
                duration_days=result.duration_days,
                bs_start=bs_start,
                bs_end=bs_end,
                days_until=days_until if days_until >= 0 else None
            )
        except Exception:
            return None
    
    def to_summary(self, festival: Festival) -> FestivalSummary:
        """Convert a Festival to FestivalSummary."""
        # Try to get next occurrence
        dates = self.get_dates(festival.id, date.today().year)
        if dates and dates.start_date < date.today():
            # Try next year
            dates = self.get_dates(festival.id, date.today().year + 1)
        
        return FestivalSummary(
            id=festival.id,
            name=festival.name,
            name_nepali=festival.name_nepali,
            tagline=festival.tagline,
            category=festival.category,
            duration_days=festival.duration_days,
            significance_level=festival.significance_level,
            is_national_holiday=festival.is_national_holiday,
            primary_color=festival.primary_color,
            next_start=dates.start_date if dates else None,
            next_end=dates.end_date if dates else None,
            days_until=dates.days_until if dates else None,
        )


# Global repository instance
_repository: Optional[FestivalRepository] = None


def get_repository() -> FestivalRepository:
    """Get or create the global repository instance."""
    global _repository
    if _repository is None:
        _repository = FestivalRepository()
    return _repository
