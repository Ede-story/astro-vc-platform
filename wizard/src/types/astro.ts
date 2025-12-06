// API Request types
export interface CalculateRequest {
  date: string;       // "1982-05-30"
  time: string;       // "09:45"
  lat: number;        // 59.93
  lon: number;        // 30.33
  timezone: number;   // 3.0
  ayanamsa: string;   // "lahiri"
  varga?: string;     // "D4"
}

// API Response types
export interface VargaSigns {
  D1: string;
  D2: string;
  D3: string;
  D4: string;
  D7: string;
  D9: string;
  D10: string;
  D12: string;
  D16: string;
  D20: string;
  D24: string;
  D27: string;
  D30: string;
  D40: string;
  D45: string;
  D60: string;
}

export interface Planet {
  name: string;
  sign: string;
  degrees: number;
  house: number;
  nakshatra: string;
  nakshatra_pada: number;
  abs_longitude: number;
  varga_signs: VargaSigns;
  // Extended data
  sign_lord: string;
  nakshatra_lord: string;
  houses_owned: number[];
  dignity: string;
  conjunctions: string[];
  aspects_giving: number[];
  aspects_receiving: string[];
}

export interface House {
  house: number;
  sign: string;
  degrees: number;
  abs_longitude: number;
  lord: string;
  occupants: string[];
  aspects_received: string[];
}

// Dignity translations
export const DIGNITY_NAMES: Record<string, string> = {
  'Exalted': 'Экзальтация',
  'Debilitated': 'Падение',
  'Own': 'Свой знак',
  'Friend': 'Дружба',
  'Neutral': 'Нейтральный',
  'Enemy': 'Вражда',
};

export interface Ascendant {
  sign: string;
  degrees: number;
  abs_longitude: number;
}

export interface VargaPlanetData {
  sign: string;
  degrees: number;
}

export interface VargaData {
  code: string;
  ascendant: string;
  ascendant_degrees?: number;
  planets: Record<string, string | VargaPlanetData>;  // Support both old and new format
}

// Digital Twin types (new architecture)
export interface DigitalTwinPlanet {
  name: string;
  sign_id: number;
  sign_name: string;
  absolute_degree: number;
  relative_degree: number;
  house_occupied: number;
  houses_owned: number[];
  nakshatra: string;
  nakshatra_lord: string;
  nakshatra_pada: number;
  sign_lord: string;
  dignity_state: string;
  aspects_giving_to: number[];
  aspects_receiving_from: string[];
  conjunctions: string[];
  is_retrograde?: boolean;
}

export interface DigitalTwinHouse {
  house_number: number;
  sign_id: number;
  sign_name: string;
  lord: string;
  occupants: string[];
  aspects_received: string[];
}

export interface DigitalTwinAscendant {
  sign_id: number;
  sign_name: string;
  degrees: number;
}

export interface VargaChart {
  ascendant: DigitalTwinAscendant;
  planets: DigitalTwinPlanet[];
  houses: DigitalTwinHouse[];
}

export interface DigitalTwinMeta {
  birth_datetime: string;
  latitude: number;
  longitude: number;
  timezone_offset: number;
  ayanamsa: string;
  ayanamsa_delta: number;
  julian_day: number;
  generated_at: string;
}

export interface DigitalTwin {
  meta: DigitalTwinMeta;
  vargas: Record<string, VargaChart>;
}

export interface CalculateResponse {
  success: boolean;
  digital_twin: DigitalTwin;
}

// Legacy types (kept for backward compatibility)
export interface LegacyCalculateResponse {
  success: boolean;
  ayanamsa: string;
  ayanamsa_delta: number;
  ascendant: Ascendant;
  planets: Planet[];
  houses: House[];
  requested_varga?: string;
  varga_data?: VargaData;
}

// UI types
export interface InputData {
  name: string;      // Profile name
  date: string;
  time: string;
  city: string;
  lat: number;
  lon: number;
  timezone: number;
  ayanamsa: string;
}

// Saved profile
export interface SavedProfile {
  id: string;
  name: string;
  created_at: string;
  input: InputData;
}

// Varga list - All 20 vargas
export const VARGA_LIST = [
  { code: 'D1', name: 'Раши (основная)' },
  { code: 'D2', name: 'Хора' },
  { code: 'D3', name: 'Дреккана' },
  { code: 'D4', name: 'Чатуртхамша' },
  { code: 'D5', name: 'Панчамша (дети)' },
  { code: 'D6', name: 'Шаштхамша (здоровье)' },
  { code: 'D7', name: 'Саптамша' },
  { code: 'D8', name: 'Аштамша (долголетие)' },
  { code: 'D9', name: 'Навамша' },
  { code: 'D10', name: 'Дашамша' },
  { code: 'D11', name: 'Рудрамша (богатство)' },
  { code: 'D12', name: 'Двадашамша' },
  { code: 'D16', name: 'Шодашамша' },
  { code: 'D20', name: 'Вимшамша' },
  { code: 'D24', name: 'Чатурвимшамша' },
  { code: 'D27', name: 'Саптавимшамша' },
  { code: 'D30', name: 'Тримшамша' },
  { code: 'D40', name: 'Кхаведамша' },
  { code: 'D45', name: 'Акшаведамша' },
  { code: 'D60', name: 'Шаштиамша' },
];

// Sign translations
export const SIGN_NAMES: Record<string, string> = {
  'Aries': 'Овен',
  'Taurus': 'Телец',
  'Gemini': 'Близнецы',
  'Cancer': 'Рак',
  'Leo': 'Лев',
  'Virgo': 'Дева',
  'Libra': 'Весы',
  'Scorpio': 'Скорпион',
  'Sagittarius': 'Стрелец',
  'Capricorn': 'Козерог',
  'Aquarius': 'Водолей',
  'Pisces': 'Рыбы',
};

// Planet translations
export const PLANET_NAMES: Record<string, string> = {
  'Sun': 'Солнце',
  'Moon': 'Луна',
  'Mars': 'Марс',
  'Mercury': 'Меркурий',
  'Jupiter': 'Юпитер',
  'Venus': 'Венера',
  'Saturn': 'Сатурн',
  'Rahu': 'Раху',
  'Ketu': 'Кету',
};

// Sign lords
export const SIGN_LORDS: Record<string, string> = {
  'Aries': 'Mars',
  'Taurus': 'Venus',
  'Gemini': 'Mercury',
  'Cancer': 'Moon',
  'Leo': 'Sun',
  'Virgo': 'Mercury',
  'Libra': 'Venus',
  'Scorpio': 'Mars',
  'Sagittarius': 'Jupiter',
  'Capricorn': 'Saturn',
  'Aquarius': 'Saturn',
  'Pisces': 'Jupiter',
};

// Vimshottari Dasha types with nested sub-periods
export interface PratyantardashaPeriod {
  lord: string;
  start_date: string;
  end_date: string;
}

export interface AntardashaPeriod {
  lord: string;
  start_date: string;
  end_date: string;
  days: number;
  pratyantardashas: PratyantardashaPeriod[];
}

export interface DashaPeriod {
  lord: string;
  years: number;
  start_date: string;
  end_date: string;
  antardashas?: AntardashaPeriod[];
}

export interface VimshottariDasha {
  birth_nakshatra: string;
  birth_nakshatra_lord: string;
  nakshatra_pada: number;
  current_mahadasha: string | null;
  current_antardasha: string | null;
  current_pratyantardasha?: string | null;
  first_dasha_balance_years: number;
  periods: DashaPeriod[];
}

// Chara Karaka types (Jaimini system)
export interface CharaKaraka {
  rank: number;
  karaka_code: string;       // AK, AmK, BK, MK, PiK, PuK, GK, DK
  karaka_name: string;       // Atmakaraka, Amatyakaraka, etc.
  karaka_meaning: string;    // Soul, Career, etc.
  planet: string;            // Sun, Moon, etc.
  degrees_in_sign: number;
  sign: string;
  house: number;
}

export interface CharaKarakas {
  karakas: CharaKaraka[];
  by_planet: Record<string, string>;   // Planet -> Karaka code
  by_karaka: Record<string, string>;   // Karaka code -> Planet
  note: string;
}

// Karaka translations
export const KARAKA_NAMES: Record<string, string> = {
  'AK': 'Атмакарака (душа)',
  'AmK': 'Аматьякарака (карьера)',
  'BK': 'Бхратрикарака (братья)',
  'MK': 'Матрикарака (мать)',
  'PiK': 'Питрикарака (отец)',
  'PuK': 'Путракарака (дети)',
  'GK': 'Гнатикарака (враги)',
  'DK': 'Даракарака (супруг)',
};

// Enhanced Digital Twin with Dasha and Karakas
export interface EnhancedDigitalTwin extends DigitalTwin {
  dasha?: VimshottariDasha;
  chara_karakas?: CharaKarakas;
}

// =============================================================================
// FULL CALCULATOR TYPES (Phase 7)
// =============================================================================

/**
 * Request for full personality calculation with LLM report
 */
export interface FullCalculatorRequest {
  date: string;       // "1982-05-30"
  time: string;       // "09:45"
  lat: number;        // 59.93
  lon: number;        // 30.33
  ayanamsa?: string;  // "lahiri" | "raman"
  generate_report?: boolean;      // Generate LLM report
  include_admin_data?: boolean;   // Include structured scores
}

/**
 * Response from full personality calculation
 */
export interface FullCalculatorResponse {
  success: boolean;
  report_text: string | null;
  admin_data: AdminData | null;
  generation_metrics: GenerationMetrics | null;
  error: string | null;
}

/**
 * LLM generation metrics
 */
export interface GenerationMetrics {
  latency_ms: number;
  model?: string;
  tokens_used?: number;
  total_time_seconds?: number;
  total_tokens?: number;
  retry_count?: number;
}

/**
 * Admin-only structured data with scores (Russian labels)
 */
export interface AdminData {
  house_scores: Record<string, number>;  // "1-й дом (Личность, тело)": 72.5
  planet_scores: Record<string, number>; // "Sun": 85.3, "Moon": 72.1, etc.
  composite_indices: Record<string, IndexScore>;
  yogas: YogaSummary;
  planets: Record<string, PlanetAdminData>;
  nakshatra_analysis: NakshatraAdminData;
  jaimini_analysis: JaiminiAdminData;
  karmic_depth: KarmicDepthData;
  timing_analysis: TimingAnalysisData;
}

/**
 * Score with level indicator
 */
export interface IndexScore {
  score: number;
  level: string;  // "высокий" | "средний" | "низкий"
}

/**
 * Yoga summary for admin panel
 */
export interface YogaSummary {
  found_yogas: YogaItem[];
  summary: {
    "Всего йог": number;
    "Раджа-йог": number;
    "Дхана-йог": number;
    "Общий балл": number;
  };
}

/**
 * Individual yoga data
 */
export interface YogaItem {
  name: string;
  category: string;
  strength: number;
  planets: string[];
}

/**
 * Planet data for admin view (Russian labels)
 */
export interface PlanetAdminData {
  sign: string;
  degree: number;
  house: number;
  dignity: string;      // "экзальтация" | "свой знак" | "падение" etc.
  retrograde: boolean;
}

/**
 * Nakshatra analysis for admin view
 */
export interface NakshatraAdminData {
  "Накшатра Луны"?: {
    name: string;
    deity: string;
    symbol: string;
    ruler: string;
  };
  "Накшатра Лагны"?: string;
}

/**
 * Jaimini analysis for admin view (Russian labels)
 */
export interface JaiminiAdminData {
  "Атмакарака"?: {
    planet: string;
    sign: string;
    meaning: string;
  };
  "Каракамша"?: {
    sign: string;
    interpretation: string;
  };
  "Чара Караки"?: Record<string, string>;  // "Атмакарака (душа)": "Moon"
}

/**
 * Karmic depth analysis
 */
export interface KarmicDepthData {
  doshas?: Array<{
    name: string;
    severity: string;
    description?: string;
  }>;
  karmic_ceiling_tier?: string;
  risk_severity_index?: number;
}

/**
 * Timing analysis (Dasha periods)
 */
export interface TimingAnalysisData {
  dasha_roadmap?: {
    current?: {
      maha_dasha: string;
      antar_dasha: string;
      end_date: string;
    };
  };
  current_dasha_quality?: string;
  is_golden_period?: boolean;
  timing_recommendation?: string;
}

/**
 * LLM Personality Report Output (from validator)
 */
export interface PersonalityReportOutput {
  personality_report: string;
  personality_summary: string;
  archetype_name: string;
  archetype_description: string;
  soul_purpose_description: string;
  life_mission_statement: string;
  public_image_description: string;
  current_period_advice: string;
  top_talents: string[];
  growth_areas: string[];
  meta?: {
    key_yoga?: string;
    dominant_element?: string;
    life_theme?: string;
  };
}
