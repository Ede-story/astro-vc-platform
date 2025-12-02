"""
AstroBrain Output Formatter for LLM

This module formats the output from AstroBrain calculator (Stages 1-12)
into a structured prompt for the LLM to generate personality reports.

The formatter extracts key data points and presents them in a clear,
organized way that the LLM can interpret effectively.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class FormattedAstroData:
    """Container for formatted astrological data ready for LLM"""
    birth_info: str
    planetary_positions: str
    gunas_elements: str
    yogas: str
    planet_strength: str
    house_analysis: str
    special_lagnas: str
    karmic_depth: str
    timing: str
    nakshatra_analysis: str
    jaimini_analysis: str

    def to_prompt(self) -> str:
        """Convert all sections to a single prompt string"""
        sections = [
            "## ДАННЫЕ РОЖДЕНИЯ",
            self.birth_info,
            "",
            "## ПЛАНЕТАРНЫЕ ПОЗИЦИИ (Stage 1-2)",
            self.planetary_positions,
            "",
            "## ГУНЫ И СТИХИИ (Stage 3-4)",
            self.gunas_elements,
            "",
            "## ЙОГИ - ОСОБЫЕ КОМБИНАЦИИ (Stage 5)",
            self.yogas,
            "",
            "## СИЛА ПЛАНЕТ (Stage 6)",
            self.planet_strength,
            "",
            "## АНАЛИЗ ДОМОВ (Stage 7)",
            self.house_analysis,
            "",
            "## СПЕЦИАЛЬНЫЕ ЛАГНЫ (Stage 8)",
            self.special_lagnas,
            "",
            "## КАРМИЧЕСКАЯ ГЛУБИНА (Stage 9)",
            self.karmic_depth,
            "",
            "## ВРЕМЕННЫЕ ПЕРИОДЫ (Stage 10)",
            self.timing,
            "",
            "## НАКШАТРЫ (Stage 11)",
            self.nakshatra_analysis,
            "",
            "## ДЖАЙМИНИ АНАЛИЗ (Stage 12)",
            self.jaimini_analysis,
        ]
        return "\n".join(sections)


class AstroDataFormatter:
    """
    Formats AstroBrain calculator output for LLM consumption.

    Takes the complex nested output from all 12 stages and creates
    a clear, structured text prompt that the LLM can interpret.
    """

    def __init__(self, calculator_output: Dict[str, Any]):
        """
        Initialize formatter with calculator output.

        Args:
            calculator_output: Full output from AstroBrain.analyze()
        """
        self.data = calculator_output
        self.digital_twin = calculator_output.get("digital_twin", {})

    def format(self) -> FormattedAstroData:
        """
        Format all calculator output into structured prompt data.

        Returns:
            FormattedAstroData with all sections formatted
        """
        return FormattedAstroData(
            birth_info=self._format_birth_info(),
            planetary_positions=self._format_planetary_positions(),
            gunas_elements=self._format_gunas_elements(),
            yogas=self._format_yogas(),
            planet_strength=self._format_planet_strength(),
            house_analysis=self._format_house_analysis(),
            special_lagnas=self._format_special_lagnas(),
            karmic_depth=self._format_karmic_depth(),
            timing=self._format_timing(),
            nakshatra_analysis=self._format_nakshatra_analysis(),
            jaimini_analysis=self._format_jaimini_analysis(),
        )

    def _format_birth_info(self) -> str:
        """Format basic birth information"""
        birth = self.digital_twin.get("birth_data", {})

        lines = []
        if birth.get("date"):
            lines.append(f"- Дата рождения: {birth['date']}")
        if birth.get("time"):
            lines.append(f"- Время рождения: {birth['time']}")
        if birth.get("location"):
            loc = birth["location"]
            lines.append(f"- Место: {loc.get('name', 'N/A')} ({loc.get('lat', 0):.2f}, {loc.get('lon', 0):.2f})")

        return "\n".join(lines) if lines else "Данные рождения не указаны"

    def _format_planetary_positions(self) -> str:
        """Format planetary positions from D1 chart"""
        d1 = self.digital_twin.get("vargas", {}).get("D1", {})
        planets = d1.get("planets", [])

        if not planets:
            return "Планетарные позиции не рассчитаны"

        lines = []
        for p in planets:
            name = p.get("name", "Unknown")
            sign = p.get("sign", "Unknown")
            house = p.get("house", 0)
            degree = p.get("degree_in_sign", 0)
            nakshatra_data = p.get("nakshatra", {})
            nakshatra = nakshatra_data.get("name", "") if isinstance(nakshatra_data, dict) else str(nakshatra_data) if nakshatra_data else ""
            retro = " (R)" if p.get("is_retrograde") else ""

            line = f"- **{name}**: {sign} ({degree:.1f}°), дом {house}{retro}"
            if nakshatra:
                line += f", накшатра {nakshatra}"
            lines.append(line)

        # Add Ascendant
        asc = d1.get("ascendant", {})
        if asc:
            lines.insert(0, f"- **Лагна (Asc)**: {asc.get('sign', 'Unknown')} ({asc.get('degree', 0):.1f}°)")

        return "\n".join(lines)

    def _format_gunas_elements(self) -> str:
        """Format Gunas and Elements analysis (Stages 3-4)"""
        gunas = self.data.get("gunas", {})
        elements = self.data.get("elements", {})

        lines = []

        # Gunas
        if gunas:
            lines.append("### Гуны (качества):")
            if "scores" in gunas:
                scores = gunas["scores"]
                lines.append(f"- Саттва: {scores.get('sattva', 0):.1%}")
                lines.append(f"- Раджас: {scores.get('rajas', 0):.1%}")
                lines.append(f"- Тамас: {scores.get('tamas', 0):.1%}")
            if "dominant" in gunas:
                lines.append(f"- Доминирующая гуна: **{gunas['dominant']}**")

        # Elements
        if elements:
            lines.append("\n### Стихии:")
            if "scores" in elements:
                scores = elements["scores"]
                for elem, score in scores.items():
                    lines.append(f"- {elem}: {score:.1%}")
            if "dominant" in elements:
                lines.append(f"- Доминирующая стихия: **{elements['dominant']}**")

        return "\n".join(lines) if lines else "Гуны и стихии не рассчитаны"

    def _format_yogas(self) -> str:
        """Format Yogas analysis (Stage 5)"""
        yogas = self.data.get("yogas", {})

        if not yogas:
            return "Йоги не рассчитаны"

        lines = []

        # Active yogas
        active = yogas.get("active_yogas", [])
        if active:
            lines.append(f"### Активные йоги ({len(active)}):")
            for yoga in active[:10]:  # Limit to top 10
                name = yoga.get("name", "Unknown")
                strength = yoga.get("strength", 0)
                description = yoga.get("description", "")
                lines.append(f"- **{name}** (сила: {strength:.0%})")
                if description:
                    lines.append(f"  {description[:200]}...")

        # Yoga summary
        summary = yogas.get("summary", {})
        if summary:
            lines.append("\n### Краткий итог:")
            if "raja_yoga_count" in summary:
                lines.append(f"- Раджа-йог: {summary['raja_yoga_count']}")
            if "dhana_yoga_count" in summary:
                lines.append(f"- Дхана-йог: {summary['dhana_yoga_count']}")
            if "overall_yoga_strength" in summary:
                lines.append(f"- Общая сила йог: {summary['overall_yoga_strength']:.0%}")

        return "\n".join(lines)

    def _format_planet_strength(self) -> str:
        """Format planet strength analysis (Stage 6)"""
        strength = self.data.get("planet_strength", {})

        if not strength:
            return "Сила планет не рассчитана"

        lines = []

        # Individual strengths
        if "planets" in strength:
            lines.append("### Сила планет (Шадбала):")
            planets = strength["planets"]

            # Sort by strength
            sorted_planets = sorted(
                planets.items(),
                key=lambda x: x[1].get("total_strength", 0) if isinstance(x[1], dict) else x[1],
                reverse=True
            )

            for name, data in sorted_planets:
                if isinstance(data, dict):
                    total = data.get("total_strength", 0)
                    status = "сильная" if total > 0.7 else "средняя" if total > 0.4 else "слабая"
                    lines.append(f"- **{name}**: {total:.0%} ({status})")
                else:
                    total = float(data)
                    status = "сильная" if total > 0.7 else "средняя" if total > 0.4 else "слабая"
                    lines.append(f"- **{name}**: {total:.0%} ({status})")

        # Strongest/weakest
        if "strongest" in strength:
            lines.append(f"\n- Сильнейшая планета: **{strength['strongest']}**")
        if "weakest" in strength:
            lines.append(f"- Слабейшая планета: **{strength['weakest']}**")

        return "\n".join(lines)

    def _format_house_analysis(self) -> str:
        """Format house analysis (Stage 7)"""
        houses = self.data.get("house_analysis", {})

        if not houses:
            return "Анализ домов не проведён"

        lines = []

        # House lords
        lords = houses.get("house_lords", {})
        if lords:
            lines.append("### Управители домов:")
            important_houses = [1, 4, 5, 7, 9, 10]  # Most important houses
            for h in important_houses:
                h_str = str(h)
                if h_str in lords:
                    lord_data = lords[h_str]
                    lord = lord_data.get("lord", "Unknown")
                    in_house = lord_data.get("in_house", 0)
                    lines.append(f"- Дом {h}: управитель {lord} в доме {in_house}")

        # Key placements
        key = houses.get("key_placements", [])
        if key:
            lines.append("\n### Ключевые расположения:")
            for placement in key[:5]:
                lines.append(f"- {placement}")

        return "\n".join(lines)

    def _format_special_lagnas(self) -> str:
        """Format special lagnas analysis (Stage 8)"""
        lagnas = self.data.get("special_lagnas", {})

        if not lagnas:
            return "Специальные лагны не рассчитаны"

        lines = ["### Специальные лагны:"]

        if "hora_lagna" in lagnas:
            lines.append(f"- Хора Лагна: {lagnas['hora_lagna']}")
        if "ghati_lagna" in lagnas:
            lines.append(f"- Гхати Лагна: {lagnas['ghati_lagna']}")
        if "bhava_lagna" in lagnas:
            lines.append(f"- Бхава Лагна: {lagnas['bhava_lagna']}")

        return "\n".join(lines)

    def _format_karmic_depth(self) -> str:
        """Format karmic depth analysis (Stage 9)"""
        karmic = self.data.get("karmic_depth", {})

        if not karmic:
            return "Кармический анализ не проведён"

        lines = []

        # Doshas
        doshas = karmic.get("doshas", [])
        if doshas:
            lines.append("### Выявленные доши:")
            for dosha in doshas:
                name = dosha.get("name", "Unknown")
                severity = dosha.get("severity", "Unknown")
                lines.append(f"- **{name}**: {severity}")
                if dosha.get("description"):
                    lines.append(f"  {dosha['description'][:150]}...")
        else:
            lines.append("### Доши: не выявлены (позитивный показатель)")

        # Karmic ceiling
        if "karmic_ceiling_tier" in karmic:
            lines.append(f"\n### Кармический потолок: {karmic['karmic_ceiling_tier']}")

        # Risk index
        if "risk_severity_index" in karmic:
            risk = karmic["risk_severity_index"]
            level = "низкий" if risk < 30 else "средний" if risk < 60 else "высокий"
            lines.append(f"- Индекс риска: {risk}/100 ({level})")

        return "\n".join(lines)

    def _format_timing(self) -> str:
        """Format timing analysis (Stage 10)"""
        timing = self.data.get("timing_analysis", {})

        if not timing:
            return "Временной анализ не проведён"

        lines = []

        # Current Dasha
        dasha = timing.get("dasha_roadmap", {})
        if dasha:
            lines.append("### Текущий период (Вимшоттари Даша):")
            current = dasha.get("current", {})
            if current:
                maha = current.get("maha_dasha", "Unknown")
                antar = current.get("antar_dasha", "Unknown")
                end_date = current.get("end_date", "Unknown")
                lines.append(f"- Маха Даша: **{maha}**")
                lines.append(f"- Антар Даша: **{antar}**")
                lines.append(f"- До: {end_date}")

        # Period quality
        if "current_dasha_quality" in timing:
            quality = timing["current_dasha_quality"]
            lines.append(f"\n### Качество периода: {quality}")

        if timing.get("is_golden_period"):
            lines.append("🌟 **ЗОЛОТОЙ ПЕРИОД** — благоприятное время для начинаний!")

        # Recommendations
        if "timing_recommendation" in timing:
            lines.append(f"\n### Рекомендация: {timing['timing_recommendation']}")

        return "\n".join(lines)

    def _format_nakshatra_analysis(self) -> str:
        """Format nakshatra analysis (Stage 11)"""
        nakshatra = self.data.get("nakshatra_analysis", {})

        if not nakshatra:
            return "Накшатра-анализ не проведён"

        lines = []

        # Moon nakshatra (most important)
        moon_nak = nakshatra.get("moon_nakshatra", {})
        if moon_nak:
            lines.append("### Накшатра Луны (Джанма Накшатра):")
            lines.append(f"- Название: **{moon_nak.get('name', 'Unknown')}**")
            if moon_nak.get("deity"):
                lines.append(f"- Божество: {moon_nak['deity']}")
            if moon_nak.get("symbol"):
                lines.append(f"- Символ: {moon_nak['symbol']}")
            if moon_nak.get("quality"):
                lines.append(f"- Качество: {moon_nak['quality']}")
            if moon_nak.get("ruling_planet"):
                lines.append(f"- Управитель: {moon_nak['ruling_planet']}")

        # Asc nakshatra
        asc_nak = nakshatra.get("asc_nakshatra", {})
        if asc_nak:
            lines.append(f"\n### Накшатра Лагны: **{asc_nak.get('name', 'Unknown')}**")

        # Archetype suggestion
        if nakshatra.get("archetype"):
            lines.append(f"\n### Предлагаемый архетип: {nakshatra['archetype']}")

        return "\n".join(lines)

    def _format_jaimini_analysis(self) -> str:
        """Format Jaimini analysis (Stage 12)"""
        jaimini = self.data.get("jaimini_analysis", {})

        if not jaimini:
            return "Джаймини-анализ не проведён"

        lines = []

        # Atmakaraka
        atma = jaimini.get("atmakaraka", {})
        if atma:
            lines.append("### Атмакарака (планета души):")
            lines.append(f"- Планета: **{atma.get('planet', 'Unknown')}**")
            if atma.get("sign"):
                lines.append(f"- Знак: {atma['sign']}")
            if atma.get("meaning"):
                lines.append(f"- Значение: {atma['meaning']}")

        # Karakamsha
        karak = jaimini.get("karakamsha", {})
        if karak:
            lines.append("\n### Каракамша (знак предназначения):")
            lines.append(f"- Знак: **{karak.get('sign', 'Unknown')}**")
            if karak.get("house"):
                lines.append(f"- Дом: {karak['house']}")
            if karak.get("interpretation"):
                lines.append(f"- Интерпретация: {karak['interpretation']}")

        # Arudha Lagna
        arudha = jaimini.get("arudha_lagna", {})
        if arudha:
            lines.append("\n### Арудха Лагна (публичный образ):")
            lines.append(f"- Знак: **{arudha.get('sign', 'Unknown')}**")
            if arudha.get("house"):
                lines.append(f"- Дом: {arudha['house']}")
            if arudha.get("interpretation"):
                lines.append(f"- Интерпретация: {arudha['interpretation']}")

        # Chara Karakas
        charas = jaimini.get("chara_karakas", {})
        if charas and isinstance(charas, dict) and charas.get("karakas"):
            lines.append("\n### Чара Караки:")
            for karaka in charas["karakas"][:7]:  # 7 karakas
                code = karaka.get("karaka_code", "")
                planet = karaka.get("planet", "")
                lines.append(f"- {code}: {planet}")

        # Soul purpose summary
        if jaimini.get("soul_purpose"):
            lines.append(f"\n### Предназначение души:")
            lines.append(jaimini["soul_purpose"])

        return "\n".join(lines)


def format_for_llm(calculator_output: Dict[str, Any]) -> str:
    """
    Convenience function to format calculator output for LLM.

    Args:
        calculator_output: Full output from AstroBrain.analyze()

    Returns:
        Formatted string ready for LLM user prompt
    """
    formatter = AstroDataFormatter(calculator_output)
    formatted = formatter.format()
    return formatted.to_prompt()
