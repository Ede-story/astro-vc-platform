'use client';

import { useState } from 'react';
import { AdminData, YogaItem, IndexScore } from '@/types/astro';

interface AdminScoresPanelProps {
  data: AdminData;
}

type TabId = 'houses' | 'indices' | 'yogas' | 'planets' | 'nakshatra' | 'jaimini' | 'karmic' | 'timing';

interface Tab {
  id: TabId;
  label: string;
}

const TABS: Tab[] = [
  { id: 'indices', label: 'Индексы' },
  { id: 'yogas', label: 'Йоги' },
  { id: 'planets', label: 'Планеты' },
  { id: 'karmic', label: 'Карма' },
  { id: 'timing', label: 'Даша' },
  { id: 'nakshatra', label: 'Накшатра' },
  { id: 'jaimini', label: 'Джаймини' },
  { id: 'houses', label: 'Дома' },
];

// Translations for composite indices
const INDEX_TRANSLATIONS: Record<string, string> = {
  'wealth': 'Богатство',
  'material_security': 'Материальная безопасность',
  'initiative': 'Инициативность',
  'communication': 'Коммуникация',
  'career': 'Карьера',
  'authority': 'Авторитет',
  'creativity': 'Креативность',
  'legacy': 'Наследие',
  'gains': 'Прибыль',
  'karmic': 'Кармический',
  'master_indices': 'Общий индекс',
};

// Russian planet names to English mapping (for score lookup)
const PLANET_RU_TO_EN: Record<string, string> = {
  'Солнце': 'Sun',
  'Луна': 'Moon',
  'Марс': 'Mars',
  'Меркурий': 'Mercury',
  'Юпитер': 'Jupiter',
  'Венера': 'Venus',
  'Сатурн': 'Saturn',
  'Раху': 'Rahu',
  'Кету': 'Ketu',
};

// Translations for dignity states
const DIGNITY_TRANSLATIONS: Record<string, string> = {
  'Exalted': 'Экзальтация',
  'Own': 'Свой знак',
  'Moolatrikona': 'Мулатрикона',
  'Friend': 'Друг',
  'Neutral': 'Нейтрально',
  'Enemy': 'Враг',
  'Debilitated': 'Падение',
};

// Translations for sign names
const SIGN_TRANSLATIONS: Record<string, string> = {
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

// Yoga category translations
const YOGA_CATEGORY_TRANSLATIONS: Record<string, string> = {
  'Raja': 'Раджа-йога',
  'Dhana': 'Дхана-йога',
  'Surya': 'Сурья-йога',
  'Negative': 'Негативная',
  'Positive': 'Позитивная',
  'Pancha Mahapurusha': 'Панча Махапуруша',
};

/**
 * Get color class based on score value (0-100)
 */
function getScoreColor(score: number): string {
  if (score >= 75) return 'text-green-600 bg-green-50';
  if (score >= 50) return 'text-blue-600 bg-blue-50';
  if (score >= 25) return 'text-yellow-600 bg-yellow-50';
  return 'text-red-600 bg-red-50';
}

/**
 * Get bar width percentage
 */
function getBarWidth(score: number): string {
  return `${Math.min(100, Math.max(0, score))}%`;
}

export default function AdminScoresPanel({ data }: AdminScoresPanelProps) {
  const [activeTab, setActiveTab] = useState<TabId>('indices');

  // DEBUG: Log all admin data received
  console.log('=== AdminScoresPanel data ===');
  console.log('Keys:', Object.keys(data));
  console.log('planet_scores:', data.planet_scores);
  console.log('planets:', data.planets);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-medium text-gray-900">
          Анализ потенциала
        </h3>
        <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
          Структурированные данные
        </span>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-4 overflow-x-auto pb-2">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-3 py-1.5 text-sm rounded-md whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[200px]">
        {activeTab === 'indices' && <IndicesTab data={data.composite_indices} />}
        {activeTab === 'yogas' && <YogasTab data={data.yogas} />}
        {activeTab === 'planets' && <PlanetsTab data={data.planets} scores={data.planet_scores} />}
        {activeTab === 'karmic' && <KarmicTab data={data.karmic_depth} />}
        {activeTab === 'timing' && <TimingTab data={data.timing_analysis} />}
        {activeTab === 'nakshatra' && <NakshatraTab data={data.nakshatra_analysis} />}
        {activeTab === 'jaimini' && <JaiminiTab data={data.jaimini_analysis} />}
        {activeTab === 'houses' && <HousesTab data={data.house_scores} />}
      </div>
    </div>
  );
}

// =============================================================================
// TAB COMPONENTS
// =============================================================================

function HousesTab({ data }: { data: Record<string, number> }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Баллы домов не рассчитаны" />;
  }

  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);

  return (
    <div className="space-y-2">
      {entries.map(([house, score]) => (
        <div key={house} className="flex items-center gap-3">
          <div className="w-48 text-sm text-gray-700 truncate" title={house}>
            {house}
          </div>
          <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${getScoreColor(score)}`}
              style={{ width: getBarWidth(score) }}
            />
          </div>
          <div className={`w-12 text-right text-sm font-medium ${getScoreColor(score)} px-1.5 py-0.5 rounded`}>
            {score.toFixed(0)}
          </div>
        </div>
      ))}
    </div>
  );
}

function IndicesTab({ data }: { data: Record<string, IndexScore | number | Record<string, unknown>> }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Композитные индексы не рассчитаны" />;
  }

  // Filter out nested objects like master_indices
  const entries = Object.entries(data).filter(([, value]) => {
    return typeof value === 'number' || (typeof value === 'object' && 'score' in (value as object));
  });

  return (
    <div className="space-y-3">
      {entries.map(([name, value]) => {
        const score = typeof value === 'number' ? value : (value as IndexScore).score;
        const level = typeof value === 'object' && 'level' in value ? (value as IndexScore).level : '';
        const translatedName = INDEX_TRANSLATIONS[name] || name;

        return (
          <div key={name} className="flex items-center gap-3">
            <div className="w-52 text-sm text-gray-700">
              {translatedName}
              {level && (
                <span className="ml-2 text-xs text-gray-400">({level})</span>
              )}
            </div>
            <div className="flex-1 h-5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${getScoreColor(score)}`}
                style={{ width: getBarWidth(score) }}
              />
            </div>
            <div className={`w-12 text-right text-sm font-medium ${getScoreColor(score)} px-1.5 py-0.5 rounded`}>
              {score.toFixed(0)}
            </div>
          </div>
        );
      })}
    </div>
  );
}

function YogasTab({ data }: { data: AdminData['yogas'] }) {
  if (!data || !data.found_yogas || data.found_yogas.length === 0) {
    return <EmptyState message="Йоги не обнаружены" />;
  }

  // Color for yoga strength
  const getYogaColor = (strength: number) => {
    if (strength >= 500) return 'text-green-600 bg-green-50';
    if (strength >= 0) return 'text-blue-600 bg-blue-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {Object.entries(data.summary).map(([label, value]) => (
          <div key={label} className="bg-gray-50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500">{label}</div>
            <div className="text-lg font-semibold text-gray-900">{typeof value === 'number' ? value.toFixed(1) : value}</div>
          </div>
        ))}
      </div>

      {/* Yoga List */}
      <div className="overflow-x-auto">
        <table className="data-table text-sm">
          <thead>
            <tr>
              <th>Йога</th>
              <th>Категория</th>
              <th>Сила</th>
              <th>Планеты</th>
            </tr>
          </thead>
          <tbody>
            {data.found_yogas.map((yoga: YogaItem, idx: number) => {
              const translatedCategory = YOGA_CATEGORY_TRANSLATIONS[yoga.category] || yoga.category;
              return (
                <tr key={idx}>
                  <td className="font-medium text-gray-900">{yoga.name}</td>
                  <td className="text-gray-500">{translatedCategory}</td>
                  <td>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getYogaColor(yoga.strength)}`}>
                      {yoga.strength > 0 ? '+' : ''}{yoga.strength}
                    </span>
                  </td>
                  <td className="text-gray-500">{yoga.planets.join(', ')}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PlanetsTab({ data, scores }: { data: Record<string, AdminData['planets'][string]>; scores?: Record<string, number> }) {
  // DEBUG: Log what PlanetsTab receives
  console.log('=== PlanetsTab ===');
  console.log('data:', data);
  console.log('scores:', scores);
  console.log('scores type:', typeof scores);
  console.log('scores keys:', scores ? Object.keys(scores) : 'N/A');

  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Данные о планетах отсутствуют" />;
  }

  // Sort entries by score (highest first) if scores available
  const entries = Object.entries(data).sort((a, b) => {
    const scoreA = scores?.[a[0]] ?? 0;
    const scoreB = scores?.[b[0]] ?? 0;
    return scoreB - scoreA;
  });

  // Get dignity color
  const getDignityColor = (dignity: string) => {
    const d = dignity.toLowerCase();
    if (d === 'exalted' || d === 'экзальтация') return 'text-green-600';
    if (d === 'own' || d === 'свой знак') return 'text-blue-600';
    if (d === 'moolatrikona' || d === 'мулатрикона') return 'text-cyan-600';
    if (d === 'friend' || d === 'друг') return 'text-teal-600';
    if (d === 'debilitated' || d === 'падение') return 'text-red-600';
    if (d === 'enemy' || d === 'враг') return 'text-orange-600';
    return 'text-gray-500';
  };

  return (
    <div className="overflow-x-auto">
      <table className="data-table text-sm">
        <thead>
          <tr>
            <th>Планета</th>
            <th>Сила</th>
            <th>Знак</th>
            <th>Дом</th>
            <th>Достоинство</th>
            <th>R</th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([planet, info]) => {
            const translatedSign = SIGN_TRANSLATIONS[info.sign] || info.sign;
            const translatedDignity = DIGNITY_TRANSLATIONS[info.dignity] || info.dignity;
            // Map Russian planet name to English for score lookup
            const englishPlanetName = PLANET_RU_TO_EN[planet] || planet;
            const score = scores?.[englishPlanetName];
            return (
              <tr key={planet}>
                <td className="font-medium text-gray-900">{planet}</td>
                <td>
                  {score !== undefined ? (
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${getScoreColor(score)}`}>
                      {score.toFixed(0)}
                    </span>
                  ) : (
                    <span className="text-gray-300">—</span>
                  )}
                </td>
                <td className="text-gray-600">{translatedSign}</td>
                <td className="text-gray-500">{info.house}</td>
                <td className={`text-sm font-medium ${getDignityColor(info.dignity)}`}>
                  {translatedDignity}
                </td>
                <td className={info.retrograde ? 'text-red-500 font-medium' : 'text-gray-300'}>
                  {info.retrograde ? 'R' : '—'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function NakshatraTab({ data }: { data: AdminData['nakshatra_analysis'] }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Накшатра-анализ не проведён" />;
  }

  const moonNak = data['Накшатра Луны'];
  const ascNak = data['Накшатра Лагны'];

  return (
    <div className="space-y-4">
      {moonNak && (
        <div className="bg-indigo-50 rounded-lg p-4">
          <div className="text-sm text-indigo-600 font-medium mb-2">
            Накшатра Луны (Джанма Накшатра)
          </div>
          <div className="text-xl font-semibold text-indigo-900 mb-3">
            {moonNak.name}
          </div>
          <div className="grid grid-cols-3 gap-3 text-sm">
            <div>
              <div className="text-gray-500">Божество</div>
              <div className="text-gray-900">{moonNak.deity || '—'}</div>
            </div>
            <div>
              <div className="text-gray-500">Символ</div>
              <div className="text-gray-900">{moonNak.symbol || '—'}</div>
            </div>
            <div>
              <div className="text-gray-500">Управитель</div>
              <div className="text-gray-900">{moonNak.ruler || '—'}</div>
            </div>
          </div>
        </div>
      )}

      {ascNak && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 font-medium mb-1">
            Накшатра Лагны
          </div>
          <div className="text-lg font-semibold text-gray-900">
            {ascNak}
          </div>
        </div>
      )}
    </div>
  );
}

function JaiminiTab({ data }: { data: AdminData['jaimini_analysis'] }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Джаймини-анализ не проведён" />;
  }

  const atma = data['Атмакарака'];
  const karakamsha = data['Каракамша'];
  const charas = data['Чара Караки'];

  return (
    <div className="space-y-4">
      {atma && (
        <div className="bg-amber-50 rounded-lg p-4">
          <div className="text-sm text-amber-600 font-medium mb-2">
            Атмакарака (Планета души)
          </div>
          <div className="text-xl font-semibold text-amber-900 mb-2">
            {atma.planet}
          </div>
          {atma.sign && (
            <div className="text-sm text-amber-700">
              Знак: {atma.sign}
            </div>
          )}
          {atma.meaning && (
            <div className="text-sm text-amber-600 mt-2">
              {atma.meaning}
            </div>
          )}
        </div>
      )}

      {karakamsha && (
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-sm text-purple-600 font-medium mb-2">
            Каракамша (Знак предназначения)
          </div>
          <div className="text-lg font-semibold text-purple-900 mb-1">
            {karakamsha.sign}
          </div>
          {karakamsha.interpretation && (
            <div className="text-sm text-purple-700">
              {karakamsha.interpretation}
            </div>
          )}
        </div>
      )}

      {charas && Object.keys(charas).length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-600 font-medium mb-3">
            Чара Караки
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(charas).map(([karaka, planet]) => (
              <div key={karaka} className="flex justify-between py-1 border-b border-gray-200 last:border-0">
                <span className="text-gray-500">{karaka}</span>
                <span className="font-medium text-gray-900">{planet}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function KarmicTab({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Кармический анализ не проведён" />;
  }

  const doshas = data.doshas || [];
  const d30 = data.d30_analysis;
  const d60 = data.d60_analysis;

  // Severity colors
  const getSeverityColor = (severity: string | number) => {
    const s = String(severity).toLowerCase();
    if (s === 'cancelled' || severity === 0) return 'text-green-600 bg-green-50';
    if (s === 'mild' || s === 'low' || (typeof severity === 'number' && severity < 3)) return 'text-yellow-600 bg-yellow-50';
    if (s === 'moderate' || s === 'medium' || (typeof severity === 'number' && severity < 6)) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="space-y-4">
      {/* D30 Analysis */}
      {d30 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm font-medium text-gray-700 mb-3">D30 Анализ (Тримшамша)</div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {d30.challenge_score !== undefined && (
              <div>
                <span className="text-gray-500">Уровень вызовов:</span>
                <span className={`ml-2 px-2 py-0.5 rounded ${getScoreColor(100 - d30.challenge_score * 10)}`}>
                  {d30.challenge_score.toFixed(1)}
                </span>
              </div>
            )}
            {d30.risk_areas && d30.risk_areas.length > 0 && (
              <div>
                <span className="text-gray-500">Зоны риска:</span>
                <span className="ml-2 text-gray-700">{d30.risk_areas.join(', ')}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* D60 Analysis */}
      {d60 && (
        <div className="bg-indigo-50 rounded-lg p-4">
          <div className="text-sm font-medium text-indigo-700 mb-3">D60 Анализ (Шаштиамша)</div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {d60.auspicious_divisions !== undefined && (
              <div>
                <span className="text-indigo-500">Благоприятных делений:</span>
                <span className="ml-2 font-medium text-indigo-900">{d60.auspicious_divisions}</span>
              </div>
            )}
            {d60.karmic_clarity !== undefined && (
              <div>
                <span className="text-indigo-500">Кармическая ясность:</span>
                <span className={`ml-2 px-2 py-0.5 rounded ${getScoreColor(d60.karmic_clarity * 10)}`}>
                  {d60.karmic_clarity.toFixed(1)}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Doshas */}
      {doshas.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">Доши</div>
          {doshas.map((dosha: {type: string; is_present: boolean; severity_level: string; severity: number; description?: string; cancellation_factors?: string[]}, idx: number) => (
            <div key={idx} className="bg-white border rounded-lg p-3">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-900">{dosha.type}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityColor(dosha.severity_level || dosha.severity)}`}>
                  {dosha.is_present ? dosha.severity_level || `${dosha.severity}` : 'Отсутствует'}
                </span>
              </div>
              {dosha.description && (
                <div className="text-xs text-gray-500 mt-1">{dosha.description}</div>
              )}
              {dosha.cancellation_factors && dosha.cancellation_factors.length > 0 && (
                <div className="text-xs text-green-600 mt-1">
                  Факторы отмены: {dosha.cancellation_factors.join(', ')}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function TimingTab({ data }: { data: any }) {
  if (!data || Object.keys(data).length === 0) {
    return <EmptyState message="Данные о таймингах не рассчитаны" />;
  }

  const roadmap = data.dasha_roadmap;
  const current = roadmap?.current;
  const quality = data.current_dasha_quality;
  const isGolden = data.is_golden_period;
  const recommendation = data.timing_recommendation;

  return (
    <div className="space-y-4">
      {/* Current Dasha */}
      {current && (
        <div className={`rounded-lg p-4 ${isGolden ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'}`}>
          <div className="flex items-center gap-2 mb-3">
            <div className="text-sm font-medium text-gray-700">Текущий период</div>
            {isGolden && (
              <span className="px-2 py-0.5 bg-yellow-200 text-yellow-800 rounded text-xs font-medium">
                Золотой период
              </span>
            )}
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-gray-500">Махадаша:</span>
              <span className="ml-2 font-medium text-gray-900">{current.maha_dasha}</span>
            </div>
            <div>
              <span className="text-gray-500">Антардаша:</span>
              <span className="ml-2 font-medium text-gray-900">{current.antar_dasha}</span>
            </div>
            {current.end_date && (
              <div className="col-span-2">
                <span className="text-gray-500">Окончание:</span>
                <span className="ml-2 text-gray-700">{current.end_date}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Quality */}
      {quality && (
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm font-medium text-blue-700 mb-2">Качество периода</div>
          <div className="text-blue-900">{quality}</div>
        </div>
      )}

      {/* Recommendation */}
      {recommendation && (
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm font-medium text-green-700 mb-2">Рекомендация</div>
          <div className="text-green-900 text-sm">{recommendation}</div>
        </div>
      )}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex items-center justify-center h-32 text-gray-400 text-sm">
      {message}
    </div>
  );
}
