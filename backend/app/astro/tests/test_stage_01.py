"""
Tests for Stage 1: Core Personality Parser

Tests the parsing of D1 chart data from digital_twin JSON.
"""

import pytest
import json
import os
from pathlib import Path

# Add parent to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.astro.calculator import AstroBrain, analyze_digital_twin
from app.astro.stages.stage_01_core import Stage01CorePersonality, BasicChartData
from app.astro.models.types import Planet, Zodiac, Dignity, House


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def sample_digital_twin():
    """
    Sample digital_twin for testing.
    Based on Vadim's birth data: 1977-10-25, 06:28, Sortavala.
    """
    return {
        "meta": {
            "birth_datetime": "1977-10-25T06:28:00",
            "latitude": 61.7,
            "longitude": 30.69,
            "timezone_offset": 3.0,
            "ayanamsa": "Raman",
            "ayanamsa_delta": 1.43
        },
        "vargas": {
            "D1": {
                "ascendant": {
                    "sign_id": 7,
                    "sign_name": "Libra",
                    "degrees": 17.84,
                    "nakshatra": "Swati",
                    "nakshatra_pada": 3,
                    "nakshatra_lord": "Rahu"
                },
                "planets": [
                    {
                        "name": "Sun",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "absolute_degree": 188.12,
                        "relative_degree": 8.12,
                        "house_occupied": 1,
                        "houses_owned": [11],
                        "nakshatra": "Swati",
                        "nakshatra_lord": "Rahu",
                        "nakshatra_pada": 1,
                        "sign_lord": "Venus",
                        "dignity_state": "Debilitated",
                        "aspects_giving_to": [7],
                        "aspects_receiving_from": ["Saturn"],
                        "conjunctions": ["Mercury"],
                        "is_retrograde": False
                    },
                    {
                        "name": "Moon",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "absolute_degree": 15.45,
                        "relative_degree": 15.45,
                        "house_occupied": 7,
                        "houses_owned": [10],
                        "nakshatra": "Bharani",
                        "nakshatra_lord": "Venus",
                        "nakshatra_pada": 2,
                        "sign_lord": "Mars",
                        "dignity_state": "Neutral",
                        "aspects_giving_to": [1],
                        "aspects_receiving_from": [],
                        "conjunctions": [],
                        "is_retrograde": False
                    },
                    {
                        "name": "Mars",
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "absolute_degree": 105.33,
                        "relative_degree": 15.33,
                        "house_occupied": 10,
                        "houses_owned": [2, 7],
                        "nakshatra": "Pushya",
                        "nakshatra_lord": "Saturn",
                        "nakshatra_pada": 3,
                        "sign_lord": "Moon",
                        "dignity_state": "Debilitated",
                        "aspects_giving_to": [1, 4, 5],
                        "aspects_receiving_from": [],
                        "conjunctions": ["Venus"],
                        "is_retrograde": False
                    },
                    {
                        "name": "Mercury",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "absolute_degree": 200.55,
                        "relative_degree": 20.55,
                        "house_occupied": 1,
                        "houses_owned": [9, 12],
                        "nakshatra": "Vishakha",
                        "nakshatra_lord": "Jupiter",
                        "nakshatra_pada": 1,
                        "sign_lord": "Venus",
                        "dignity_state": "Friend",
                        "aspects_giving_to": [7],
                        "aspects_receiving_from": [],
                        "conjunctions": ["Sun"],
                        "is_retrograde": False
                    },
                    {
                        "name": "Jupiter",
                        "sign_id": 6,
                        "sign_name": "Virgo",
                        "absolute_degree": 168.22,
                        "relative_degree": 18.22,
                        "house_occupied": 12,
                        "houses_owned": [3, 6],
                        "nakshatra": "Hasta",
                        "nakshatra_lord": "Moon",
                        "nakshatra_pada": 3,
                        "sign_lord": "Mercury",
                        "dignity_state": "Enemy",
                        "aspects_giving_to": [4, 6, 8],
                        "aspects_receiving_from": [],
                        "conjunctions": [],
                        "is_retrograde": True
                    },
                    {
                        "name": "Venus",
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "absolute_degree": 112.44,
                        "relative_degree": 22.44,
                        "house_occupied": 10,
                        "houses_owned": [1, 8],
                        "nakshatra": "Ashlesha",
                        "nakshatra_lord": "Mercury",
                        "nakshatra_pada": 4,
                        "sign_lord": "Moon",
                        "dignity_state": "Neutral",
                        "aspects_giving_to": [4],
                        "aspects_receiving_from": ["Saturn"],
                        "conjunctions": ["Mars"],
                        "is_retrograde": False
                    },
                    {
                        "name": "Saturn",
                        "sign_id": 5,
                        "sign_name": "Leo",
                        "absolute_degree": 143.88,
                        "relative_degree": 23.88,
                        "house_occupied": 11,
                        "houses_owned": [4, 5],
                        "nakshatra": "Purva Phalguni",
                        "nakshatra_lord": "Venus",
                        "nakshatra_pada": 4,
                        "sign_lord": "Sun",
                        "dignity_state": "Enemy",
                        "aspects_giving_to": [1, 5, 8],
                        "aspects_receiving_from": [],
                        "conjunctions": [],
                        "is_retrograde": True
                    },
                    {
                        "name": "Rahu",
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "absolute_degree": 183.67,
                        "relative_degree": 3.67,
                        "house_occupied": 1,
                        "houses_owned": [],
                        "nakshatra": "Chitra",
                        "nakshatra_lord": "Mars",
                        "nakshatra_pada": 4,
                        "sign_lord": "Venus",
                        "dignity_state": "Neutral",
                        "aspects_giving_to": [],
                        "aspects_receiving_from": [],
                        "conjunctions": [],
                        "is_retrograde": True
                    },
                    {
                        "name": "Ketu",
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "absolute_degree": 3.67,
                        "relative_degree": 3.67,
                        "house_occupied": 7,
                        "houses_owned": [],
                        "nakshatra": "Ashwini",
                        "nakshatra_lord": "Ketu",
                        "nakshatra_pada": 2,
                        "sign_lord": "Mars",
                        "dignity_state": "Neutral",
                        "aspects_giving_to": [],
                        "aspects_receiving_from": [],
                        "conjunctions": [],
                        "is_retrograde": True
                    }
                ],
                "houses": [
                    {
                        "house_number": 1,
                        "sign_id": 7,
                        "sign_name": "Libra",
                        "lord": "Venus",
                        "occupants": ["Sun", "Mercury", "Rahu"],
                        "aspects_received": ["Saturn"]
                    },
                    {
                        "house_number": 2,
                        "sign_id": 8,
                        "sign_name": "Scorpio",
                        "lord": "Mars",
                        "occupants": [],
                        "aspects_received": []
                    },
                    {
                        "house_number": 3,
                        "sign_id": 9,
                        "sign_name": "Sagittarius",
                        "lord": "Jupiter",
                        "occupants": [],
                        "aspects_received": []
                    },
                    {
                        "house_number": 4,
                        "sign_id": 10,
                        "sign_name": "Capricorn",
                        "lord": "Saturn",
                        "occupants": [],
                        "aspects_received": ["Jupiter", "Mars"]
                    },
                    {
                        "house_number": 5,
                        "sign_id": 11,
                        "sign_name": "Aquarius",
                        "lord": "Saturn",
                        "occupants": [],
                        "aspects_received": ["Saturn", "Mars"]
                    },
                    {
                        "house_number": 6,
                        "sign_id": 12,
                        "sign_name": "Pisces",
                        "lord": "Jupiter",
                        "occupants": [],
                        "aspects_received": ["Jupiter"]
                    },
                    {
                        "house_number": 7,
                        "sign_id": 1,
                        "sign_name": "Aries",
                        "lord": "Mars",
                        "occupants": ["Moon", "Ketu"],
                        "aspects_received": ["Sun", "Mercury"]
                    },
                    {
                        "house_number": 8,
                        "sign_id": 2,
                        "sign_name": "Taurus",
                        "lord": "Venus",
                        "occupants": [],
                        "aspects_received": ["Jupiter", "Saturn"]
                    },
                    {
                        "house_number": 9,
                        "sign_id": 3,
                        "sign_name": "Gemini",
                        "lord": "Mercury",
                        "occupants": [],
                        "aspects_received": []
                    },
                    {
                        "house_number": 10,
                        "sign_id": 4,
                        "sign_name": "Cancer",
                        "lord": "Moon",
                        "occupants": ["Mars", "Venus"],
                        "aspects_received": []
                    },
                    {
                        "house_number": 11,
                        "sign_id": 5,
                        "sign_name": "Leo",
                        "lord": "Sun",
                        "occupants": ["Saturn"],
                        "aspects_received": []
                    },
                    {
                        "house_number": 12,
                        "sign_id": 6,
                        "sign_name": "Virgo",
                        "lord": "Mercury",
                        "occupants": ["Jupiter"],
                        "aspects_received": []
                    }
                ]
            }
        }
    }


# =============================================================================
# TESTS
# =============================================================================

class TestStage01Parsing:
    """Tests for Stage 1 parsing functionality"""

    def test_parse_ascendant(self, sample_digital_twin):
        """Test ascendant parsing"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        assert result.ascendant.sign == Zodiac.LIBRA
        assert result.ascendant.lord == Planet.VENUS
        assert 17 < result.ascendant.degree < 18

    def test_parse_sun_sign(self, sample_digital_twin):
        """Test Sun sign extraction"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        assert result.sun_sign == "Libra"

    def test_parse_moon_sign(self, sample_digital_twin):
        """Test Moon sign extraction"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        assert result.moon_sign == "Aries"

    def test_parse_all_planets(self, sample_digital_twin):
        """Test all 9 planets are parsed"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        assert len(result.planets) == 9
        planet_names = [p.name for p in result.planets]
        assert "Sun" in planet_names
        assert "Moon" in planet_names
        assert "Rahu" in planet_names
        assert "Ketu" in planet_names

    def test_debilitated_planets_detected(self, sample_digital_twin):
        """Test debilitated planets are identified"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        # Sun in Libra and Mars in Cancer should be debilitated
        debilitated = [p for p in result.planets if p.dignity == "Debilitated"]
        assert len(debilitated) >= 2

    def test_house_lords_extracted(self, sample_digital_twin):
        """Test house lords are extracted correctly"""
        stage = Stage01CorePersonality(sample_digital_twin)
        result = stage.parse()

        # House 1 lord should be Venus (Libra)
        assert result.house_lords[1]["lord"] == "Venus"
        # House 10 lord should be Moon (Cancer)
        assert result.house_lords[10]["lord"] == "Moon"


class TestAstroBrain:
    """Tests for main AstroBrain calculator"""

    def test_basic_analysis(self, sample_digital_twin):
        """Test basic analysis run"""
        brain = AstroBrain(sample_digital_twin)
        output = brain.analyze()

        assert output.basic_chart is not None
        assert 1 in output.stages_completed

    def test_output_to_dict(self, sample_digital_twin):
        """Test output serialization to dict"""
        brain = AstroBrain(sample_digital_twin)
        output = brain.analyze()

        result = output.to_dict()

        assert "basic_chart" in result
        assert "version" in result
        assert "stages_completed" in result

    def test_output_to_json(self, sample_digital_twin):
        """Test output serialization to JSON"""
        brain = AstroBrain(sample_digital_twin)
        output = brain.analyze()

        json_str = output.to_json()

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "basic_chart" in parsed

    def test_convenience_methods(self, sample_digital_twin):
        """Test convenience methods"""
        brain = AstroBrain(sample_digital_twin)
        brain.analyze()

        # Test getters
        assert brain.get_ascendant_sign() == Zodiac.LIBRA
        assert brain.get_moon_sign() == "Aries"
        assert len(brain.get_strongest_planets()) > 0


class TestDignities:
    """Tests for dignity reference data"""

    def test_exaltation_data(self):
        """Test exaltation data is correct"""
        from app.astro.reference.dignities import EXALTATION

        assert EXALTATION[Planet.SUN] == Zodiac.ARIES
        assert EXALTATION[Planet.MOON] == Zodiac.TAURUS
        assert EXALTATION[Planet.JUPITER] == Zodiac.CANCER

    def test_debilitation_data(self):
        """Test debilitation data is correct"""
        from app.astro.reference.dignities import DEBILITATION

        assert DEBILITATION[Planet.SUN] == Zodiac.LIBRA
        assert DEBILITATION[Planet.MARS] == Zodiac.CANCER

    def test_is_exalted(self):
        """Test is_exalted function"""
        from app.astro.reference.dignities import is_exalted

        assert is_exalted(Planet.SUN, Zodiac.ARIES) == True
        assert is_exalted(Planet.SUN, Zodiac.LIBRA) == False

    def test_is_debilitated(self):
        """Test is_debilitated function"""
        from app.astro.reference.dignities import is_debilitated

        assert is_debilitated(Planet.SUN, Zodiac.LIBRA) == True
        assert is_debilitated(Planet.SUN, Zodiac.ARIES) == False


class TestFriendships:
    """Tests for friendship reference data"""

    def test_natural_friends(self):
        """Test natural friends data"""
        from app.astro.reference.friendships import NATURAL_FRIENDS

        assert Planet.MOON in NATURAL_FRIENDS[Planet.SUN]
        assert Planet.MARS in NATURAL_FRIENDS[Planet.SUN]

    def test_natural_enemies(self):
        """Test natural enemies data"""
        from app.astro.reference.friendships import NATURAL_ENEMIES

        assert Planet.SATURN in NATURAL_ENEMIES[Planet.SUN]
        assert Planet.VENUS in NATURAL_ENEMIES[Planet.SUN]

    def test_natural_relationship(self):
        """Test get_natural_relationship function"""
        from app.astro.reference.friendships import get_natural_relationship

        assert get_natural_relationship(Planet.SUN, Planet.MOON) == "friend"
        assert get_natural_relationship(Planet.SUN, Planet.SATURN) == "enemy"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
