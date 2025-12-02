"""
AstroBrain - Main 12-Stage Calculator

This is the main entry point for the astrological analysis.
It orchestrates all 12 stages and produces the CalculatorOutput
ready for LLM interpretation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import json

from .stages.stage_01_core import Stage01CorePersonality, BasicChartData
from .stages.stage_02_soul import Stage02SoulBlueprint, Stage2Result
from .stages.stage_03_yogas import Stage03YogaAnalysis, Stage3Result
from .stages.stage_04_wealth import Stage04WealthAnalysis, Stage4Result
from .stages.stage_05_skills import Stage05SkillsAnalysis, Stage5Result
from .stages.stage_06_career import Stage06CareerAnalysis, Stage6Result
from .stages.stage_07_creativity import Stage07CreativityAnalysis, Stage7Result
from .stages.stage_08_profit import Stage08ProfitAnalysis, Stage8Result
from .stages.stage_09_karmic import Stage09KarmicAnalysis, Stage9Result
from .stages.stage_10_timing import Stage10TimingAnalysis, Stage10Result
from .formulas.indices import calculate_composite_indices, get_life_area_interpretations
from .models.types import Planet, Zodiac, House


@dataclass
class CalculatorOutput:
    """
    Complete output from the 12-stage calculator.

    This structure is designed for LLM interpretation.
    All sections are optional to allow partial analysis.
    """
    # Section 1: Basic Chart Data (from Stage 1)
    basic_chart: Optional[BasicChartData] = None

    # Section 2: Soul Blueprint (from Stage 2)
    soul_blueprint: Optional[Dict[str, Any]] = None

    # Section 3: Yogas (from Stage 3)
    yogas: Optional[Dict[str, Any]] = None

    # Section 4: Wealth & Assets (from Stage 4 - D2, D4)
    wealth_assets: Optional[Dict[str, Any]] = None

    # Section 5: Skills & Initiative (from Stage 5 - D3)
    skills_initiative: Optional[Dict[str, Any]] = None

    # Section 6: Career & Status (from Stage 6 - D10)
    career_status: Optional[Dict[str, Any]] = None

    # Section 7: Creativity & Legacy (from Stage 7 - D5, D7)
    creativity_legacy: Optional[Dict[str, Any]] = None

    # Section 8: Profit & Expansion (from Stage 8 - D11, D12)
    profit_expansion: Optional[Dict[str, Any]] = None

    # Section 9: Karmic Depth (from Stage 9 - D30, D60)
    karmic_depth: Optional[Dict[str, Any]] = None

    # Section 10: Timing Analysis (from Stage 10 - Dasha, Ashtakavarga)
    timing_analysis: Optional[Dict[str, Any]] = None

    # Section 11: Composite Indices (calculated from Stages 4-8)
    composite_indices: Optional[Dict[str, Any]] = None

    # Section 12: Life Area Interpretations
    life_areas: Optional[Dict[str, Any]] = None

    # Section 13: LLM Guidance
    llm_guidance: Optional[Dict[str, Any]] = None

    # Metadata
    version: str = "1.0.0"
    stages_completed: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = {
            "version": self.version,
            "stages_completed": self.stages_completed,
        }

        if self.basic_chart:
            result["basic_chart"] = self.basic_chart.to_dict()

        if self.soul_blueprint:
            result["soul_blueprint"] = self.soul_blueprint

        if self.yogas:
            result["yogas"] = self.yogas

        if self.wealth_assets:
            result["wealth_assets"] = self.wealth_assets

        if self.skills_initiative:
            result["skills_initiative"] = self.skills_initiative

        if self.career_status:
            result["career_status"] = self.career_status

        if self.creativity_legacy:
            result["creativity_legacy"] = self.creativity_legacy

        if self.profit_expansion:
            result["profit_expansion"] = self.profit_expansion

        if self.karmic_depth:
            result["karmic_depth"] = self.karmic_depth

        if self.timing_analysis:
            result["timing_analysis"] = self.timing_analysis

        if self.composite_indices:
            result["composite_indices"] = self.composite_indices

        if self.life_areas:
            result["life_areas"] = self.life_areas

        if self.llm_guidance:
            result["llm_guidance"] = self.llm_guidance

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class AstroBrain:
    """
    Main calculator class that orchestrates all 12 analysis stages.

    Usage:
        brain = AstroBrain(digital_twin)
        output = brain.analyze()
        # or
        output = brain.analyze_stage(1)  # Just Stage 1
    """

    def __init__(self, digital_twin: Dict[str, Any]):
        """
        Initialize AstroBrain with a digital_twin JSON.

        Args:
            digital_twin: The digital_twin dict from the astro API
        """
        self.digital_twin = digital_twin
        self.output = CalculatorOutput()

        # Stage instances (lazy loaded)
        self._stage1: Optional[Stage01CorePersonality] = None
        self._stage2: Optional[Stage02SoulBlueprint] = None
        self._stage3: Optional[Stage03YogaAnalysis] = None
        self._stage4: Optional[Stage04WealthAnalysis] = None
        self._stage5: Optional[Stage05SkillsAnalysis] = None
        self._stage6: Optional[Stage06CareerAnalysis] = None
        self._stage7: Optional[Stage07CreativityAnalysis] = None
        self._stage8: Optional[Stage08ProfitAnalysis] = None
        self._stage9: Optional[Stage09KarmicAnalysis] = None
        self._stage10: Optional[Stage10TimingAnalysis] = None

        # Cached results for inter-stage dependencies
        self._d1_planets: Optional[List] = None
        self._d1_house_scores: Optional[Dict[str, float]] = None
        self._d1_house_lords: Optional[Dict[int, Dict[str, Any]]] = None

        # Stage results cache for composite index calculation
        self._stage4_result: Optional[Dict[str, Any]] = None
        self._stage5_result: Optional[Dict[str, Any]] = None
        self._stage6_result: Optional[Dict[str, Any]] = None
        self._stage7_result: Optional[Dict[str, Any]] = None
        self._stage8_result: Optional[Dict[str, Any]] = None
        self._d9_synergy: float = 50.0

    @classmethod
    def from_json(cls, json_str: str) -> "AstroBrain":
        """Create AstroBrain from JSON string"""
        data = json.loads(json_str)
        return cls(data)

    @classmethod
    def from_file(cls, filepath: str) -> "AstroBrain":
        """Create AstroBrain from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(data)

    @property
    def stage1(self) -> Stage01CorePersonality:
        """Get or create Stage 1 parser"""
        if self._stage1 is None:
            self._stage1 = Stage01CorePersonality(self.digital_twin)
        return self._stage1

    def analyze(self, stages: Optional[List[int]] = None) -> CalculatorOutput:
        """
        Run specified analysis stages.

        Args:
            stages: List of stage numbers to run (1-12).
                   If None, runs all available stages.

        Returns:
            CalculatorOutput with results from all requested stages
        """
        if stages is None:
            # Run all available stages (1-10 implemented)
            stages = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        for stage_num in sorted(stages):
            self.analyze_stage(stage_num)

        # Calculate composite indices if stages 4-8 were run
        if all(s in self.output.stages_completed for s in [4, 5, 6, 7, 8]):
            self._calculate_composite_indices()

        return self.output

    def analyze_stage(self, stage_num: int) -> CalculatorOutput:
        """
        Run a specific analysis stage.

        Args:
            stage_num: Stage number (1-12)

        Returns:
            CalculatorOutput with this stage's results added
        """
        if stage_num == 1:
            self._run_stage_1()
        elif stage_num == 2:
            self._run_stage_2()
        elif stage_num == 3:
            self._run_stage_3()
        elif stage_num == 4:
            self._run_stage_4()
        elif stage_num == 5:
            self._run_stage_5()
        elif stage_num == 6:
            self._run_stage_6()
        elif stage_num == 7:
            self._run_stage_7()
        elif stage_num == 8:
            self._run_stage_8()
        elif stage_num == 9:
            self._run_stage_9()
        elif stage_num == 10:
            self._run_stage_10()
        # ... stages 11-12 to be implemented

        return self.output

    def _run_stage_1(self) -> None:
        """
        Stage 1: Core Personality (D1 Chart)

        Parses basic chart data and extracts:
        - Ascendant info
        - Sun and Moon signs
        - All planet positions
        - House lords
        - Strongest/weakest planets
        """
        basic_chart = self.stage1.parse()
        self.output.basic_chart = basic_chart
        self.output.stages_completed.append(1)

    def _run_stage_2(self) -> None:
        """
        Stage 2: Soul Blueprint (D9 Navamsha)

        Analyzes:
        - D9 chart positions
        - Vargottama planets
        - D1-D9 synergy score
        - Adjusted house scores
        """
        # Ensure Stage 1 is run first
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        # Get D1 data from Stage 1
        if self._d1_planets is None:
            self._d1_planets = self.output.basic_chart.planets
            self._d1_house_scores = self.output.basic_chart.house_scores

        stage2 = Stage02SoulBlueprint(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_scores
        )
        result = stage2.analyze()

        # Convert to dict for output
        self.output.soul_blueprint = {
            "d9_ascendant": result.d9_ascendant.name,
            "d9_ascendant_degree": result.d9_ascendant_degree,
            "vargottama_planets": [
                {"planet": v.planet.value, "sign": v.sign.name}
                for v in result.vargottama_planets
            ],
            "synergy_score": result.synergy_score,
            "synergy_level": result.synergy_level.value,
            "house_scores_adjusted": result.house_scores_adjusted,
            "confirmations": result.confirmations,
            "contradictions": result.contradictions,
            "atmakaraka": result.atmakaraka.value if result.atmakaraka else None,
            "atmakaraka_d9_sign": result.atmakaraka_d9_sign.name if result.atmakaraka_d9_sign else None,
        }
        self.output.stages_completed.append(2)

    def _run_stage_3(self) -> None:
        """
        Stage 3: Yoga Detection

        Analyzes:
        - Raja Yogas, Dhana Yogas, etc.
        - Neecha Bhanga Raja Yoga
        - Overall yoga score
        """
        # Ensure Stage 1 is run first
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        if self._d1_planets is None:
            self._d1_planets = self.output.basic_chart.planets

        ascendant_sign = self.output.basic_chart.ascendant.sign

        stage3 = Stage03YogaAnalysis(self._d1_planets, ascendant_sign)
        result = stage3.analyze()

        # Convert to dict for output
        self.output.yogas = {
            "yogas_found": [
                {
                    "name": y.name,
                    "sanskrit_name": y.sanskrit_name,
                    "category": y.category.value,
                    "strength": y.strength,
                    "participating_planets": [p.value for p in y.participating_planets],
                    "interpretation_key": y.interpretation_key,
                    "timing_activation": y.timing_activation,
                }
                for y in result.yogas
            ],
            "neecha_bhanga": {
                planet: {
                    "debilitation_sign": nb.debilitation_sign.name,
                    "cancellation_level": nb.cancellation_level.value,
                    "rules_satisfied": nb.rules_satisfied,
                    "effective_dignity": nb.effective_dignity,
                }
                for planet, nb in result.neecha_bhanga.items()
            },
            "summary": {
                "total_count": result.yoga_summary.total_count,
                "positive_count": result.yoga_summary.positive_count,
                "negative_count": result.yoga_summary.negative_count,
                "raja_yoga_count": result.yoga_summary.raja_yoga_count,
                "dhana_yoga_count": result.yoga_summary.dhana_yoga_count,
                "mahapurusha_yogas": result.yoga_summary.mahapurusha_yogas,
                "key_yogas": result.yoga_summary.key_yogas,
                "overall_yoga_score": result.yoga_summary.overall_yoga_score,
            },
            "house_yoga_bonuses": result.house_yoga_bonuses,
        }
        self.output.stages_completed.append(3)

    def _run_stage_4(self) -> None:
        """
        Stage 4: Wealth & Assets (D2 Hora + D4 Chaturthamsha)

        Analyzes:
        - D2 chart for wealth accumulation
        - D4 chart for fixed assets
        - Financial stability indicators
        """
        # Ensure Stage 1 is run first
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage4 = Stage04WealthAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage4.analyze()

        # Store for composite indices
        self._stage4_result = result.to_dict()
        self.output.wealth_assets = self._stage4_result
        self.output.stages_completed.append(4)

    def _run_stage_5(self) -> None:
        """
        Stage 5: Skills & Initiative (D3 Drekkana)

        Analyzes:
        - Courage and initiative
        - Communication skills
        - Siblings and short journeys
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage5 = Stage05SkillsAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage5.analyze()

        self._stage5_result = result.to_dict()
        self.output.skills_initiative = self._stage5_result
        self.output.stages_completed.append(5)

    def _run_stage_6(self) -> None:
        """
        Stage 6: Career & Status (D10 Dashamsha)

        Analyzes:
        - Career potential and archetypes
        - Professional success indicators
        - Authority and recognition
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage6 = Stage06CareerAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage6.analyze()

        self._stage6_result = result.to_dict()
        self.output.career_status = self._stage6_result
        self.output.stages_completed.append(6)

    def _run_stage_7(self) -> None:
        """
        Stage 7: Creativity & Legacy (D5 Panchamsha + D7 Saptamsha)

        Analyzes:
        - Creative potential
        - Progeny and legacy
        - Intellectual abilities
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage7 = Stage07CreativityAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage7.analyze()

        self._stage7_result = result.to_dict()
        self.output.creativity_legacy = self._stage7_result
        self.output.stages_completed.append(7)

    def _run_stage_8(self) -> None:
        """
        Stage 8: Profit & Expansion (D11 Rudramsha + D12 Dwadashamsha)

        Analyzes:
        - Gains and networking
        - Karmic patterns
        - Ancestral influences
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage8 = Stage08ProfitAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage8.analyze()

        self._stage8_result = result.to_dict()
        self.output.profit_expansion = self._stage8_result
        self.output.stages_completed.append(8)

    def _run_stage_9(self) -> None:
        """
        Stage 9: Karmic Depth (D30 Trimshamsha + D60 Shashtiamsha)

        Analyzes:
        - Dosha detection (Mangal, Kala Sarpa, Guru Chandal, etc.)
        - D30 risk analysis
        - D60 karmic ceiling
        - Risk severity index
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage9 = Stage09KarmicAnalysis(
            self.digital_twin,
            self._d1_planets,
            self._d1_house_lords
        )
        result = stage9.analyze()

        self.output.karmic_depth = result.to_dict()
        self.output.stages_completed.append(9)

    def _run_stage_10(self) -> None:
        """
        Stage 10: Timing Analysis (Vimshottari Dasha + Ashtakavarga)

        Analyzes:
        - Current and upcoming dasha periods
        - Dasha roadmap
        - Ashtakavarga scores
        - Investment timing recommendations
        - Golden periods identification
        """
        if 1 not in self.output.stages_completed:
            self._run_stage_1()

        self._ensure_d1_data()

        stage10 = Stage10TimingAnalysis(
            self.digital_twin,
            self._d1_planets
        )
        result = stage10.analyze()

        self.output.timing_analysis = result.to_dict()
        self.output.stages_completed.append(10)

    def _ensure_d1_data(self) -> None:
        """Ensure D1 data is cached for stage dependencies"""
        if self._d1_planets is None:
            self._d1_planets = self.output.basic_chart.planets
        if self._d1_house_scores is None:
            self._d1_house_scores = self.output.basic_chart.house_scores
        if self._d1_house_lords is None:
            self._d1_house_lords = self.output.basic_chart.house_lords

        # Get D9 synergy from Stage 2 if available
        if 2 in self.output.stages_completed and self.output.soul_blueprint:
            self._d9_synergy = self.output.soul_blueprint.get("synergy_score", 50.0)

    def _calculate_composite_indices(self) -> None:
        """Calculate composite indices from Stages 4-8 results"""
        indices = calculate_composite_indices(
            stage4_result=self._stage4_result,
            stage5_result=self._stage5_result,
            stage6_result=self._stage6_result,
            stage7_result=self._stage7_result,
            stage8_result=self._stage8_result,
            d9_synergy=self._d9_synergy
        )

        self.output.composite_indices = indices.to_dict()

        # Generate life area interpretations
        life_areas = get_life_area_interpretations(indices)
        self.output.life_areas = {
            area: {
                "name": data.name,
                "score": round(data.score, 1),
                "confidence": data.confidence,
                "factors": data.contributing_factors,
                "interpretation": data.interpretation
            }
            for area, data in life_areas.items()
        }

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def get_planet(self, planet: Planet):
        """Get planet position from Stage 1 analysis"""
        return self.stage1.get_planet(planet)

    def get_house(self, house: House):
        """Get house data from Stage 1 analysis"""
        return self.stage1.get_house(house)

    def get_ascendant_sign(self) -> Optional[Zodiac]:
        """Get ascendant sign"""
        if self.output.basic_chart:
            return self.output.basic_chart.ascendant.sign
        return None

    def get_moon_sign(self) -> Optional[str]:
        """Get moon sign (rashi)"""
        if self.output.basic_chart:
            return self.output.basic_chart.moon_sign
        return None

    def get_strongest_planets(self) -> List[str]:
        """Get list of strongest planets by dignity"""
        if self.output.basic_chart:
            return self.output.basic_chart.strongest_planets
        return []

    def get_weakest_planets(self) -> List[str]:
        """Get list of weakest planets by dignity"""
        if self.output.basic_chart:
            return self.output.basic_chart.weakest_planets
        return []


def analyze_digital_twin(digital_twin: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to analyze a digital_twin.

    Args:
        digital_twin: The digital_twin JSON dict

    Returns:
        Dictionary with analysis results
    """
    brain = AstroBrain(digital_twin)
    output = brain.analyze()
    return output.to_dict()
