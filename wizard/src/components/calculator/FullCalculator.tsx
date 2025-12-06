'use client';

import { useState, useEffect, useRef } from 'react';
import DatePicker, { registerLocale } from 'react-datepicker';
import { ru } from 'date-fns/locale';
import Link from 'next/link';
import 'react-datepicker/dist/react-datepicker.css';

import AdminScoresPanel from './AdminScoresPanel';
import PersonalityReport from './PersonalityReport';
import {
  FullCalculatorRequest,
  FullCalculatorResponse,
  AdminData,
  GenerationMetrics
} from '@/types/astro';
import { useAuth } from '@/hooks/useAuth';

// Register Russian locale for date picker
registerLocale('ru', ru);

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface BirthData {
  name: string;
  date: string;
  time: string;
  city: string;
  lat: number;
  lon: number;
  ayanamsa: string;
}

const DEFAULT_BIRTH_DATA: BirthData = {
  name: '',
  date: '1977-10-25',
  time: '06:28',
  city: 'Sortavala',
  lat: 61.70,
  lon: 30.69,
  ayanamsa: 'lahiri',
};

export default function FullCalculator() {
  // Auth state
  const { user, isAuthenticated } = useAuth();

  // Form state
  const [birthData, setBirthData] = useState<BirthData>(DEFAULT_BIRTH_DATA);
  const [isFormCollapsed, setIsFormCollapsed] = useState(false);

  // API state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Result state
  const [reportText, setReportText] = useState<string | null>(null);
  const [adminData, setAdminData] = useState<AdminData | null>(null);
  const [generationMetrics, setGenerationMetrics] = useState<GenerationMetrics | null>(null);

  // City search state
  const [citySuggestions, setCitySuggestions] = useState<Array<{
    display_name: string;
    lat: string;
    lon: string;
  }>>([]);
  const [citySearchLoading, setCitySearchLoading] = useState(false);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);
  const [isTypingCity, setIsTypingCity] = useState(false);
  const cityInputRef = useRef<HTMLDivElement>(null);

  // Close city suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (cityInputRef.current && !cityInputRef.current.contains(event.target as Node)) {
        setShowCitySuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced city search
  useEffect(() => {
    if (!isTypingCity) return;

    const timeoutId = setTimeout(() => {
      if (birthData.city && birthData.city.length >= 2) {
        searchCity(birthData.city);
      }
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [birthData.city, isTypingCity]);

  const searchCity = async (query: string) => {
    if (query.length < 2) {
      setCitySuggestions([]);
      setShowCitySuggestions(false);
      return;
    }

    setCitySearchLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&accept-language=ru&addressdetails=1&featuretype=city`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          }
        }
      );
      if (response.ok) {
        const data = await response.json();
        setCitySuggestions(data);
        setShowCitySuggestions(data.length > 0);
      }
    } catch (err) {
      console.error('City search failed:', err);
    } finally {
      setCitySearchLoading(false);
    }
  };

  const selectCity = (suggestion: { display_name: string; lat: string; lon: string }) => {
    const cityName = suggestion.display_name.split(',')[0].trim();
    const lat = parseFloat(suggestion.lat);
    const lon = parseFloat(suggestion.lon);

    setBirthData(prev => ({
      ...prev,
      city: cityName,
      lat: lat,
      lon: lon,
    }));
    setShowCitySuggestions(false);
    setCitySuggestions([]);
    setIsTypingCity(false);
  };

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);
    setReportText(null);
    setAdminData(null);
    setGenerationMetrics(null);

    try {
      // Always include admin data for planet scores display
      const includeAdminData = true;

      const request: FullCalculatorRequest = {
        date: birthData.date,
        time: birthData.time,
        lat: birthData.lat,
        lon: birthData.lon,
        ayanamsa: birthData.ayanamsa,
        generate_report: true,
        include_admin_data: includeAdminData,
      };

      const response = await fetch(`${API_URL}/v1/full-calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: FullCalculatorResponse = await response.json();

      if (data.success) {
        // DEBUG: Log admin_data and planet_scores
        console.log('=== API Response ===');
        console.log('admin_data:', data.admin_data);
        console.log('planet_scores:', data.admin_data?.planet_scores);

        setReportText(data.report_text || null);
        setAdminData(data.admin_data || null);
        setGenerationMetrics(data.generation_metrics || null);
        setIsFormCollapsed(true);

        if (data.error) {
          // Partial success - show warning
          console.warn('Calculation warning:', data.error);
        }
      } else {
        throw new Error(data.error || 'Calculation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка расчета');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string): string => {
    const [year, month, day] = dateStr.split('-');
    return `${day}.${month}.${year}`;
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <Link href="/dashboard" className="block hover:opacity-80 transition-opacity">
              <h1 className="text-2xl font-semibold text-gray-900">
                StarMeet
              </h1>
              <p className="text-gray-500 text-sm mt-1">Анализ личности</p>
            </Link>
          </div>
          <div>
            {isAuthenticated ? (
              <Link
                href="/dashboard"
                className="text-sm text-gray-600 hover:text-gray-900"
              >
                {user?.email}
              </Link>
            ) : (
              <Link
                href="/login"
                className="text-sm text-brand-green hover:text-brand-green-hover"
              >
                Войти
              </Link>
            )}
          </div>
        </header>

        {/* Collapsed Form Summary */}
        {isFormCollapsed && (reportText || adminData) && (
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  {birthData.name && (
                    <>
                      <span className="font-semibold text-gray-900">{birthData.name}</span>
                      <span className="text-gray-400 mx-2">|</span>
                    </>
                  )}
                  <span className="font-medium text-gray-900">{birthData.city}</span>
                  <span className="text-gray-400 mx-2">|</span>
                  <span className="text-gray-600">{formatDate(birthData.date)} {birthData.time}</span>
                  <span className="text-gray-400 mx-2">|</span>
                  <span className="text-gray-500">{birthData.lat.toFixed(2)}°, {birthData.lon.toFixed(2)}°</span>
                </div>
              </div>
              <button
                onClick={() => {
                  setIsFormCollapsed(false);
                  setIsTypingCity(false);
                  setCitySuggestions([]);
                  setShowCitySuggestions(false);
                }}
                className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                Изменить
              </button>
            </div>
          </div>
        )}

        {/* Expanded Input Form */}
        {!isFormCollapsed && (
          <div className="card mb-6">
            <h2 className="text-base font-medium text-gray-900 mb-4">Данные рождения</h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <label className="input-label">Имя (опционально)</label>
                <input
                  type="text"
                  className="input-field"
                  value={birthData.name}
                  placeholder="Например: Вадим"
                  onChange={(e) => setBirthData({ ...birthData, name: e.target.value })}
                />
              </div>

              <div>
                <label className="input-label">Дата рождения</label>
                <DatePicker
                  selected={birthData.date ? new Date(birthData.date) : null}
                  onChange={(date: Date | null) => {
                    if (date) {
                      const year = date.getFullYear();
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const day = String(date.getDate()).padStart(2, '0');
                      setBirthData({ ...birthData, date: `${year}-${month}-${day}` });
                    }
                  }}
                  dateFormat="dd.MM.yyyy"
                  locale="ru"
                  showYearDropdown
                  showMonthDropdown
                  dropdownMode="select"
                  yearDropdownItemNumber={100}
                  scrollableYearDropdown
                  maxDate={new Date()}
                  minDate={new Date(1900, 0, 1)}
                  placeholderText="Выберите дату"
                  className="input-field w-full"
                  wrapperClassName="w-full"
                />
              </div>

              <div>
                <label className="input-label">Время</label>
                <input
                  type="time"
                  className="input-field"
                  value={birthData.time}
                  onChange={(e) => setBirthData({ ...birthData, time: e.target.value })}
                />
              </div>

              <div className="relative" ref={cityInputRef}>
                <label className="input-label">Город</label>
                <input
                  type="text"
                  className="input-field"
                  value={birthData.city}
                  placeholder="Начните вводить город..."
                  onChange={(e) => {
                    setIsTypingCity(true);
                    setBirthData({ ...birthData, city: e.target.value });
                  }}
                  onFocus={() => {
                    if (isTypingCity && citySuggestions.length > 0) {
                      setShowCitySuggestions(true);
                    }
                  }}
                />
                {citySearchLoading && (
                  <div className="absolute right-3 top-8 text-gray-400">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                )}
                {showCitySuggestions && citySuggestions.length > 0 && (
                  <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-xl max-h-48 overflow-y-auto">
                    {citySuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        type="button"
                        className="w-full px-3 py-2 text-left text-sm text-gray-800 hover:bg-gray-100 border-b border-gray-200 last:border-0"
                        onClick={() => selectCity(suggestion)}
                      >
                        {suggestion.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="input-label">Широта</label>
                <input
                  type="number"
                  className="input-field"
                  value={birthData.lat}
                  onChange={(e) => setBirthData({ ...birthData, lat: parseFloat(e.target.value) })}
                  step="0.01"
                />
              </div>

              <div>
                <label className="input-label">Долгота</label>
                <input
                  type="number"
                  className="input-field"
                  value={birthData.lon}
                  onChange={(e) => setBirthData({ ...birthData, lon: parseFloat(e.target.value) })}
                  step="0.01"
                />
              </div>

              <div>
                <label className="input-label">Аянамса</label>
                <select
                  className="input-field"
                  value={birthData.ayanamsa}
                  onChange={(e) => setBirthData({ ...birthData, ayanamsa: e.target.value })}
                >
                  <option value="lahiri">Lahiri (Chitrapaksha)</option>
                  <option value="raman">Raman (B.V. Raman)</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end">
              <button
                onClick={handleCalculate}
                disabled={loading}
                className="bg-brand-graphite text-white font-medium py-2.5 px-8 rounded-md hover:bg-brand-graphite-hover transition-colors duration-150 text-sm disabled:opacity-50 flex items-center gap-2"
              >
                {loading ? (
                  <>
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Генерация отчёта...
                  </>
                ) : (
                  'Сгенерировать отчёт'
                )}
              </button>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
                {error}
              </div>
            )}
          </div>
        )}

        {/* Results */}
        {(reportText || adminData || loading) && (
          <div className="space-y-6">
            {/* Personality Report */}
            <PersonalityReport
              reportText={reportText || ''}
              loading={loading}
              error={error && !reportText ? error : undefined}
            />

            {/* Admin Panel - always show when data is available */}
            {adminData && (
              <AdminScoresPanel data={adminData} />
            )}

            {/* Generation Metrics (debug info) */}
            {generationMetrics && isAuthenticated && (
              <div className="card bg-gray-50">
                <h3 className="text-sm font-medium text-gray-700 mb-2">Метрики генерации</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs text-gray-500">
                  <div>
                    <span className="block text-gray-400">Время</span>
                    <span className="font-mono">
                      {typeof generationMetrics.total_time_seconds === 'number'
                        ? `${generationMetrics.total_time_seconds.toFixed(1)}s`
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-gray-400">Токены</span>
                    <span className="font-mono">
                      {generationMetrics.total_tokens ?? generationMetrics.tokens_used ?? 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-gray-400">Модель</span>
                    <span className="font-mono">
                      {generationMetrics.model ?? 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="block text-gray-400">Попыток</span>
                    <span className="font-mono">
                      {generationMetrics.retry_count ?? 0}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Empty state */}
        {!loading && !reportText && !adminData && !error && isFormCollapsed && (
          <div className="card text-center py-12 text-gray-500">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Введите данные рождения и нажмите &quot;Сгенерировать отчёт&quot;</p>
          </div>
        )}
      </div>
    </div>
  );
}
