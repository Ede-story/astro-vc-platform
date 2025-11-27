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

export interface VargaData {
  code: string;
  ascendant: string;
  planets: Record<string, string>;
}

export interface CalculateResponse {
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

// Varga list
export const VARGA_LIST = [
  { code: 'D1', name: 'Раши (основная)' },
  { code: 'D2', name: 'Хора' },
  { code: 'D3', name: 'Дреккана' },
  { code: 'D4', name: 'Чатуртхамша' },
  { code: 'D7', name: 'Саптамша' },
  { code: 'D9', name: 'Навамша' },
  { code: 'D10', name: 'Дашамша' },
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
