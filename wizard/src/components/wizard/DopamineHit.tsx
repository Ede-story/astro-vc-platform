'use client';

import { useEffect, useState } from 'react';
import { DigitalTwin } from '@/types/astro';

// Sign to Russian name
const SIGN_NAMES: Record<string, string> = {
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

// Sign characteristics for hook generation
const SIGN_TRAITS: Record<string, { element: string; quality: string; traits: string[] }> = {
  'Aries': { element: 'fire', quality: 'cardinal', traits: ['лидерство', 'энергия', 'инициатива'] },
  'Taurus': { element: 'earth', quality: 'fixed', traits: ['стабильность', 'надёжность', 'практичность'] },
  'Gemini': { element: 'air', quality: 'mutable', traits: ['коммуникабельность', 'любознательность', 'адаптивность'] },
  'Cancer': { element: 'water', quality: 'cardinal', traits: ['эмоциональность', 'забота', 'интуиция'] },
  'Leo': { element: 'fire', quality: 'fixed', traits: ['харизма', 'творчество', 'щедрость'] },
  'Virgo': { element: 'earth', quality: 'mutable', traits: ['аналитичность', 'внимание к деталям', 'служение'] },
  'Libra': { element: 'air', quality: 'cardinal', traits: ['гармония', 'дипломатия', 'эстетика'] },
  'Scorpio': { element: 'water', quality: 'fixed', traits: ['глубина', 'трансформация', 'проницательность'] },
  'Sagittarius': { element: 'fire', quality: 'mutable', traits: ['философия', 'оптимизм', 'свобода'] },
  'Capricorn': { element: 'earth', quality: 'cardinal', traits: ['амбиции', 'дисциплина', 'достижения'] },
  'Aquarius': { element: 'air', quality: 'fixed', traits: ['инновации', 'независимость', 'гуманизм'] },
  'Pisces': { element: 'water', quality: 'mutable', traits: ['творчество', 'эмпатия', 'духовность'] },
};

// Generate personalized hook text
function generateHookText(sunSign: string, moonSign: string, ascSign: string): string {
  const sun = SIGN_TRAITS[sunSign];
  const moon = SIGN_TRAITS[moonSign];
  const asc = SIGN_TRAITS[ascSign];

  if (!sun || !moon || !asc) return '';

  // Check for rare combinations
  const elements = [sun.element, moon.element, asc.element];
  const uniqueElements = new Set(elements);

  if (uniqueElements.size === 3) {
    return `Редкая комбинация: ${sun.traits[0]} + ${moon.traits[1]} + ${asc.traits[0]}. Вы объединяете разные стихии в уникальный баланс.`;
  }

  if (sun.element === moon.element && moon.element === asc.element) {
    const elementNames: Record<string, string> = {
      fire: 'огненная',
      earth: 'земная',
      air: 'воздушная',
      water: 'водная',
    };
    return `Мощная ${elementNames[sun.element]} энергия: ${sun.traits[0]}, ${moon.traits[1]} и ${asc.traits[0]} создают целостный характер.`;
  }

  return `${sun.traits[0].charAt(0).toUpperCase() + sun.traits[0].slice(1)} в сочетании с ${moon.traits[1]} и ${asc.traits[0]} — это ваша уникальная формула.`;
}

interface DopamineHitProps {
  digitalTwin: DigitalTwin;
  onContinue: () => void;
}

export default function DopamineHit({ digitalTwin, onContinue }: DopamineHitProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [showHook, setShowHook] = useState(false);

  // Get main placements from D1
  const d1 = digitalTwin.vargas?.D1;
  const planets = d1?.planets || [];

  const sun = planets.find(p => p.name === 'Sun');
  const moon = planets.find(p => p.name === 'Moon');
  const ascendant = d1?.ascendant;

  const sunSign = sun?.sign_name || 'Aries';
  const moonSign = moon?.sign_name || 'Aries';
  const ascSign = ascendant?.sign_name || 'Aries';

  const hookText = generateHookText(sunSign, moonSign, ascSign);

  useEffect(() => {
    // Stagger animation
    setTimeout(() => setIsVisible(true), 100);
    setTimeout(() => setShowDetails(true), 600);
    setTimeout(() => setShowHook(true), 1200);
  }, []);

  return (
    <div className="text-center py-12">
      {/* Title */}
      <div
        className={`transition-all duration-700 transform ${
          isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <div className="text-4xl mb-4">✨</div>
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Ваш астрологический портрет
        </h1>
      </div>

      {/* Main placements */}
      <div
        className={`mt-8 space-y-4 transition-all duration-700 delay-300 transform ${
          showDetails ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        {/* Sun */}
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 inline-block mx-auto">
          <div className="flex items-center justify-center gap-4">
            <span className="text-4xl">☀️</span>
            <div className="text-left">
              <div className="text-sm text-gray-500">Солнце</div>
              <div className="text-xl font-semibold text-gray-900">
                {SIGN_NAMES[sunSign] || sunSign}
              </div>
            </div>
          </div>
        </div>

        {/* Moon */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-6 inline-block mx-auto">
          <div className="flex items-center justify-center gap-4">
            <span className="text-4xl">🌙</span>
            <div className="text-left">
              <div className="text-sm text-gray-500">Луна</div>
              <div className="text-xl font-semibold text-gray-900">
                {SIGN_NAMES[moonSign] || moonSign}
              </div>
            </div>
          </div>
        </div>

        {/* Ascendant */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 inline-block mx-auto">
          <div className="flex items-center justify-center gap-4">
            <span className="text-4xl">⬆️</span>
            <div className="text-left">
              <div className="text-sm text-gray-500">Асцендент</div>
              <div className="text-xl font-semibold text-gray-900">
                {SIGN_NAMES[ascSign] || ascSign}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hook text */}
      <div
        className={`mt-8 max-w-md mx-auto transition-all duration-700 delay-500 transform ${
          showHook ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <p className="text-gray-600 italic leading-relaxed">
          "{hookText}"
        </p>
      </div>

      {/* Continue button */}
      <div
        className={`mt-10 transition-all duration-700 delay-700 transform ${
          showHook ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
        }`}
      >
        <button
          onClick={onContinue}
          className="bg-brand-graphite text-white font-medium py-4 px-8 rounded-xl hover:bg-brand-graphite-hover transition-colors duration-150 text-lg inline-flex items-center gap-2"
        >
          Продолжить
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}
