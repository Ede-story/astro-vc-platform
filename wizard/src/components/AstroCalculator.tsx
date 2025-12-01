'use client';

import { useState, useEffect, useRef, Fragment } from 'react';
import { useSearchParams } from 'next/navigation';
import DatePicker, { registerLocale } from 'react-datepicker';
import { ru } from 'date-fns/locale';
import Link from 'next/link';
import 'react-datepicker/dist/react-datepicker.css';
import {
  DigitalTwin,
  VargaChart,
  InputData,
  SavedProfile,
  VARGA_LIST,
  SIGN_NAMES,
  PLANET_NAMES,
  DIGNITY_NAMES,
  KARAKA_NAMES,
  EnhancedDigitalTwin,
  VimshottariDasha,
  CharaKarakas,
  DashaPeriod,
  AntardashaPeriod
} from '@/types/astro';
import TableColumnSelector, {
  ColumnConfig,
  DEFAULT_PLANET_COLUMNS,
  DEFAULT_HOUSE_COLUMNS
} from './TableColumnSelector';
import { useAuth } from '@/hooks/useAuth';
import { createClient } from '@/lib/supabase/client';

// Register Russian locale for date picker
registerLocale('ru', ru);

// Default input with RAMAN ayanamsa
// Timezone is AUTO-DETECTED by backend - not editable by user
const DEFAULT_INPUT: InputData = {
  name: '',
  date: '1982-05-30',
  time: '09:45',
  city: 'Санкт-Петербург',
  lat: 59.93,
  lon: 30.33,
  timezone: 0, // Display only - auto-detected by backend
  ayanamsa: 'raman',
};

// Timezone info returned by backend
interface DetectedTimezone {
  timezone_name: string;
  utc_offset: number;
  is_dst: boolean;
  source: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Debug log - will show in browser console
if (typeof window !== 'undefined') {
  console.log('[StarMeet] API_URL:', API_URL);
  console.log('[StarMeet] NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL);
}

export default function AstroCalculator() {
  const searchParams = useSearchParams();
  const [input, setInput] = useState<InputData>(DEFAULT_INPUT);
  const [selectedVarga, setSelectedVarga] = useState('D1');

  // Single state for the entire Digital Twin (enhanced with Dasha + Karakas)
  const [digitalTwin, setDigitalTwin] = useState<EnhancedDigitalTwin | null>(null);

  // Timezone detected by backend (read-only display)
  const [detectedTimezone, setDetectedTimezone] = useState<DetectedTimezone | null>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Auth state
  const { user, isAuthenticated } = useAuth();
  const supabase = createClient();

  // Load profile from URL parameter
  const [profileLoaded, setProfileLoaded] = useState(false);

  // Collapsible form state
  const [isFormCollapsed, setIsFormCollapsed] = useState(false);

  // Column visibility state
  const [planetColumns, setPlanetColumns] = useState<ColumnConfig[]>(DEFAULT_PLANET_COLUMNS);
  const [houseColumns, setHouseColumns] = useState<ColumnConfig[]>(DEFAULT_HOUSE_COLUMNS);

  // Saved profiles state
  const [savedProfiles, setSavedProfiles] = useState<SavedProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);

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

  // Dasha expansion state
  const [expandedMahadasha, setExpandedMahadasha] = useState<string | null>(null);
  const [expandedAntardasha, setExpandedAntardasha] = useState<string | null>(null);

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

  // Load profile from URL parameter (?profile=UUID)
  useEffect(() => {
    const loadProfileFromUrl = async () => {
      const profileId = searchParams.get('profile');
      if (!profileId || profileLoaded) return;

      try {
        const { data: profile, error } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', profileId)
          .single();

        if (error || !profile) {
          console.error('Failed to load profile:', error);
          return;
        }

        // Set input data from profile
        setInput({
          name: profile.name || '',
          date: profile.birth_date || DEFAULT_INPUT.date,
          time: profile.birth_time || DEFAULT_INPUT.time,
          city: profile.birth_city || DEFAULT_INPUT.city,
          lat: profile.birth_latitude || DEFAULT_INPUT.lat,
          lon: profile.birth_longitude || DEFAULT_INPUT.lon,
          timezone: profile.birth_timezone || 0,
          ayanamsa: profile.ayanamsa || 'raman',
        });

        // Set digital twin if available
        if (profile.digital_twin) {
          setDigitalTwin(profile.digital_twin);
          setIsFormCollapsed(true);
        }

        setActiveProfileId(profileId);
        setProfileLoaded(true);
      } catch (err) {
        console.error('Error loading profile:', err);
      }
    };

    loadProfileFromUrl();
  }, [searchParams, profileLoaded, supabase]);

  // Search city coordinates using Nominatim API
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

  // Debounced city search
  useEffect(() => {
    if (!isTypingCity) return;

    const timeoutId = setTimeout(() => {
      if (input.city && input.city.length >= 2) {
        searchCity(input.city);
      }
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [input.city, isTypingCity]);

  // Select city from suggestions (timezone will be auto-detected by backend on calculate)
  const selectCity = (suggestion: { display_name: string; lat: string; lon: string }) => {
    const cityName = suggestion.display_name.split(',')[0].trim();
    const lat = parseFloat(suggestion.lat);
    const lon = parseFloat(suggestion.lon);

    setInput(prev => ({
      ...prev,
      city: cityName,
      lat: lat,
      lon: lon,
    }));
    setShowCitySuggestions(false);
    setCitySuggestions([]);
    setIsTypingCity(false);
  };

  // Load profiles when user changes
  useEffect(() => {
    if (user) {
      loadProfiles();
    } else {
      setSavedProfiles([]);
    }
  }, [user]);

  const loadProfiles = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('id, name, created_at')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

      if (data) {
        setSavedProfiles(data.map(p => ({
          id: p.id,
          name: p.name,
          created_at: p.created_at,
          input: {} as InputData, // Will be loaded on select
        })));
      }
    } catch (err) {
      console.error('Failed to load profiles:', err);
    }
  };

  const loadProfile = async (profileId: string) => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', profileId)
        .single();

      if (data) {
        // Load input data from profile
        setInput({
          name: data.name || '',
          date: data.birth_date || DEFAULT_INPUT.date,
          time: data.birth_time || DEFAULT_INPUT.time,
          city: data.birth_city || DEFAULT_INPUT.city,
          lat: data.birth_latitude || DEFAULT_INPUT.lat,
          lon: data.birth_longitude || DEFAULT_INPUT.lon,
          timezone: data.birth_timezone || DEFAULT_INPUT.timezone,
          ayanamsa: data.ayanamsa || DEFAULT_INPUT.ayanamsa,
        });
        // Load Digital Twin if available
        if (data.digital_twin) {
          setDigitalTwin(data.digital_twin as DigitalTwin);
          setIsFormCollapsed(true);
        }
        setActiveProfileId(profileId);
      }
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const deleteProfile = async (profileId: string) => {
    if (!confirm('Удалить этот профиль?')) return;

    try {
      const { error } = await supabase
        .from('profiles')
        .delete()
        .eq('id', profileId);

      if (!error) {
        setSavedProfiles((prev: SavedProfile[]) => prev.filter((p: SavedProfile) => p.id !== profileId));
        if (activeProfileId === profileId) {
          setActiveProfileId(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete profile:', err);
    }
  };

  // REMOVED: useEffect for selectedVarga - NO more API calls on varga switch!

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      // Backend Authority: timezone is auto-detected, we don't send it
      const response = await fetch(`${API_URL}/v1/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: input.date,
          time: input.time,
          lat: input.lat,
          lon: input.lon,
          ayanamsa: input.ayanamsa,
          // timezone_override: optional, for experts only
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      // Debug: Log FULL API response to verify sub-periods
      console.log('[StarMeet] ==========================================');
      console.log('[StarMeet] FULL API RESPONSE:', JSON.stringify(data.digital_twin?.dasha?.periods?.[0], null, 2));
      console.log('[StarMeet] ==========================================');
      console.log('[StarMeet] API Response received');
      console.log('[StarMeet] Has digital_twin:', !!data.digital_twin);
      console.log('[StarMeet] Has dasha:', !!data.digital_twin?.dasha);
      console.log('[StarMeet] Dasha periods:', data.digital_twin?.dasha?.periods?.length);
      console.log('[StarMeet] First period:', data.digital_twin?.dasha?.periods?.[0]);
      console.log('[StarMeet] First period antardashas count:', data.digital_twin?.dasha?.periods?.[0]?.antardashas?.length);
      console.log('[StarMeet] First period antardashas:', data.digital_twin?.dasha?.periods?.[0]?.antardashas);

      if (data.success && data.digital_twin) {
        // CRITICAL DEBUG: Alert the user about antardashas count
        const antCount = data.digital_twin?.dasha?.periods?.[0]?.antardashas?.length || 0;
        console.log('[StarMeet] SETTING STATE - antardashas count:', antCount);
        if (antCount === 0) {
          console.error('[StarMeet] WARNING: API returned 0 antardashas!');
        }
        setDigitalTwin(data.digital_twin);
        // Save detected timezone info for display
        if (data.detected_timezone) {
          setDetectedTimezone(data.detected_timezone);
          // Update input.timezone for display purposes
          setInput(prev => ({ ...prev, timezone: data.detected_timezone.utc_offset }));
        }
        setIsFormCollapsed(true);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка расчета');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!digitalTwin) return;
    if (!input.name.trim()) {
      alert('Введите имя профиля');
      return;
    }

    // If not authenticated, redirect to login
    if (!isAuthenticated || !user) {
      alert('Войдите в аккаунт, чтобы сохранить профиль');
      return;
    }

    setSaveStatus('saving');
    try {
      // Save to Supabase
      const { data, error } = await supabase
        .from('profiles')
        .insert({
          user_id: user.id,
          name: input.name,
          birth_date: input.date,
          birth_time: input.time,
          birth_city: input.city,
          birth_latitude: input.lat,
          birth_longitude: input.lon,
          birth_timezone: input.timezone,
          ayanamsa: input.ayanamsa,
          digital_twin: digitalTwin,
        })
        .select()
        .single();

      if (error) {
        console.error('Save error:', error);
        setSaveStatus('error');
      } else {
        setSaveStatus('saved');
        setActiveProfileId(data.id);
        await loadProfiles();
        setTimeout(() => setSaveStatus(null), 3000);
      }
    } catch {
      setSaveStatus('error');
    }
  };

  // Format date for display
  const formatDate = (dateStr: string): string => {
    const [year, month, day] = dateStr.split('-');
    return `${day}.${month}.${year}`;
  };

  // Get active chart for selected varga - INSTANT, no API call
  const activeChart: VargaChart | null = digitalTwin?.vargas?.[selectedVarga] || null;

  // Get current ascendant based on selected varga
  const getCurrentAscendant = (): string => {
    if (!activeChart) return '';
    const sign = SIGN_NAMES[activeChart.ascendant.sign_name] || activeChart.ascendant.sign_name;
    return `${sign} ${activeChart.ascendant.degrees.toFixed(2)}°`;
  };

  // Check if column is visible
  const isColumnVisible = (columns: ColumnConfig[], id: string): boolean => {
    return columns.find(c => c.id === id)?.enabled ?? false;
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              StarMeet
            </h1>
            <p className="text-gray-500 text-sm mt-1">Ведический астрологический калькулятор</p>
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

        {/* Saved Profiles Row */}
        <div className="card mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                setInput({ name: '', date: '', time: '', city: '', lat: 0, lon: 0, timezone: 3, ayanamsa: 'raman' });
                setDigitalTwin(null);
                setActiveProfileId(null);
                setIsFormCollapsed(false);
                setCitySuggestions([]);
                setShowCitySuggestions(false);
              }}
              className="bg-white text-gray-700 font-medium py-2 px-4 rounded-md border border-gray-200
                         hover:bg-gray-50 hover:border-gray-300 transition-colors duration-150 text-sm whitespace-nowrap"
            >
              + Новый профиль
            </button>

            <div className="flex items-center gap-1 ml-1">
              <select
                className="bg-transparent border-0 text-gray-700 text-sm py-1 pr-6 focus:outline-none focus:ring-0 cursor-pointer"
                value={activeProfileId || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value) {
                    loadProfile(value);
                  }
                }}
                style={{
                  backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`,
                  backgroundPosition: 'right 0 center',
                  backgroundRepeat: 'no-repeat',
                  backgroundSize: '1.25em 1.25em',
                  WebkitAppearance: 'none',
                  MozAppearance: 'none',
                  appearance: 'none',
                }}
              >
                <option value="">Выберите профиль</option>
                {savedProfiles.filter((p: SavedProfile) => p.name && p.name.trim() !== '').map((profile: SavedProfile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>

              {activeProfileId && (
                <button
                  onClick={() => deleteProfile(activeProfileId)}
                  className="p-1 text-gray-400 hover:text-gray-500 transition-colors"
                  title="Удалить профиль"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Collapsed Form Summary */}
        {isFormCollapsed && digitalTwin && (
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-sm">
                  {input.name && (
                    <>
                      <span className="font-semibold text-gray-900">{input.name}</span>
                      <span className="text-gray-400 mx-2">|</span>
                    </>
                  )}
                  <span className="font-medium text-gray-900">{input.city}</span>
                  <span className="text-gray-400 mx-2">|</span>
                  <span className="text-gray-600">{formatDate(input.date)} {input.time}</span>
                  <span className="text-gray-400 mx-2">|</span>
                  <span className="text-gray-500">{input.lat.toFixed(2)}°, {input.lon.toFixed(2)}°</span>
                  {/* Timezone Badge (auto-detected) */}
                  {detectedTimezone && (
                    <>
                      <span className="text-gray-400 mx-2">|</span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        UTC{detectedTimezone.utc_offset >= 0 ? '+' : ''}{detectedTimezone.utc_offset}
                        {detectedTimezone.is_dst && ' (DST)'}
                      </span>
                    </>
                  )}
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
                <label className="input-label">Имя профиля</label>
                <input
                  type="text"
                  className="input-field"
                  value={input.name}
                  placeholder="Например: Олег"
                  onChange={(e) => setInput({ ...input, name: e.target.value })}
                />
              </div>

              <div>
                <label className="input-label">Дата рождения</label>
                <DatePicker
                  selected={input.date ? new Date(input.date) : null}
                  onChange={(date: Date | null) => {
                    if (date) {
                      const year = date.getFullYear();
                      const month = String(date.getMonth() + 1).padStart(2, '0');
                      const day = String(date.getDate()).padStart(2, '0');
                      setInput({ ...input, date: `${year}-${month}-${day}` });
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
                  value={input.time}
                  onChange={(e) => setInput({ ...input, time: e.target.value })}
                />
              </div>

              <div className="relative" ref={cityInputRef}>
                <label className="input-label">Город</label>
                <input
                  type="text"
                  className="input-field"
                  value={input.city}
                  placeholder="Начните вводить город..."
                  onChange={(e) => {
                    setIsTypingCity(true);
                    setInput({ ...input, city: e.target.value });
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
                  value={input.lat}
                  onChange={(e) => setInput({ ...input, lat: parseFloat(e.target.value) })}
                  step="0.01"
                />
              </div>

              <div>
                <label className="input-label">Долгота</label>
                <input
                  type="number"
                  className="input-field"
                  value={input.lon}
                  onChange={(e) => setInput({ ...input, lon: parseFloat(e.target.value) })}
                  step="0.01"
                />
              </div>

              <div>
                <label className="input-label">Аянамса</label>
                <select
                  className="input-field"
                  value={input.ayanamsa}
                  onChange={(e) => setInput({ ...input, ayanamsa: e.target.value })}
                >
                  <option value="raman">Raman (B.V. Raman)</option>
                  <option value="lahiri">Lahiri (Chitrapaksha)</option>
                  <option value="krishnamurti">Krishnamurti (KP)</option>
                </select>
              </div>

              <div className="flex items-end gap-2">
                <button
                  onClick={handleCalculate}
                  disabled={loading}
                  className="bg-brand-graphite text-white font-medium py-2.5 px-5 rounded-md hover:bg-brand-graphite-hover transition-colors duration-150 text-sm flex-1 disabled:opacity-50"
                >
                  {loading ? 'Расчет...' : 'Рассчитать'}
                </button>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
                {error}
              </div>
            )}
          </div>
        )}

        {/* Results */}
        {digitalTwin && activeChart && (
          <>
            {/* Varga Selector */}
            <div className="card mb-6">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-700">Варга:</label>
                  <select
                    className="input-field w-auto"
                    value={selectedVarga}
                    onChange={(e) => setSelectedVarga(e.target.value)}
                  >
                    {VARGA_LIST.map((v) => (
                      <option key={v.code} value={v.code}>
                        {v.code} - {v.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="text-sm text-gray-500">
                  Асцендент:{' '}
                  <span className="font-medium text-gray-900">
                    {getCurrentAscendant()}
                  </span>
                </div>

                <div className="ml-auto flex gap-2">
                  {isAuthenticated ? (
                    <button
                      onClick={handleSave}
                      disabled={saveStatus === 'saving'}
                      className="btn-secondary"
                    >
                      {saveStatus === 'saving' ? 'Сохранение...' :
                       saveStatus === 'saved' ? 'Сохранено!' :
                       saveStatus === 'error' ? 'Ошибка' :
                       'Сохранить профиль'}
                    </button>
                  ) : (
                    <Link
                      href="/login"
                      className="btn-secondary"
                    >
                      Войти для сохранения
                    </Link>
                  )}
                </div>
              </div>
            </div>

            {/* Data Tables */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Planetary Details */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-medium text-gray-900">
                    Планеты ({selectedVarga})
                  </h3>
                  <TableColumnSelector
                    columns={planetColumns}
                    onChange={setPlanetColumns}
                  />
                </div>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {isColumnVisible(planetColumns, 'name') && <th>Планета</th>}
                        {isColumnVisible(planetColumns, 'sign') && <th>Знак</th>}
                        {isColumnVisible(planetColumns, 'degrees') && <th>Градусы</th>}
                        {isColumnVisible(planetColumns, 'retrograde') && <th>R</th>}
                        {isColumnVisible(planetColumns, 'nakshatra') && <th>Накшатра</th>}
                        {isColumnVisible(planetColumns, 'house') && <th>Дом</th>}
                        {isColumnVisible(planetColumns, 'sign_lord') && <th>Упр. знака</th>}
                        {isColumnVisible(planetColumns, 'nakshatra_lord') && <th>Упр. накш.</th>}
                        {isColumnVisible(planetColumns, 'houses_owned') && <th>Управляет</th>}
                        {isColumnVisible(planetColumns, 'dignity') && <th>Достоинство</th>}
                        {isColumnVisible(planetColumns, 'conjunctions') && <th>Соединения</th>}
                        {isColumnVisible(planetColumns, 'aspects_giving') && <th>Аспекты</th>}
                        {isColumnVisible(planetColumns, 'aspects_receiving') && <th>Аспект от</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {activeChart.planets.map((planet) => (
                        <tr key={planet.name}>
                          {isColumnVisible(planetColumns, 'name') && (
                            <td className="font-medium text-gray-900">
                              {PLANET_NAMES[planet.name] || planet.name}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'sign') && (
                            <td>
                              {SIGN_NAMES[planet.sign_name] || planet.sign_name}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'degrees') && (
                            <td className="text-gray-600">
                              {planet.relative_degree.toFixed(2)}°
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'retrograde') && (
                            <td className={planet.is_retrograde ? 'text-red-500 font-medium' : 'text-gray-300'}>
                              {planet.is_retrograde ? 'R' : '—'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'nakshatra') && (
                            <td className={selectedVarga === 'D1' ? 'text-gray-600' : 'text-gray-400'}>
                              {planet.nakshatra}
                              <span className="text-gray-400 ml-1">
                                ({planet.nakshatra_pada})
                              </span>
                              {selectedVarga !== 'D1' && (
                                <span className="text-gray-300 ml-1 text-xs">(D1)</span>
                              )}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'house') && (
                            <td>{planet.house_occupied}</td>
                          )}
                          {isColumnVisible(planetColumns, 'sign_lord') && (
                            <td className="text-gray-500">
                              {PLANET_NAMES[planet.sign_lord] || planet.sign_lord || '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'nakshatra_lord') && (
                            <td className="text-gray-500">
                              {PLANET_NAMES[planet.nakshatra_lord] || planet.nakshatra_lord || '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'houses_owned') && (
                            <td className="text-gray-500">
                              {planet.houses_owned?.length > 0 ? planet.houses_owned.join(', ') : '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'dignity') && (
                            <td className={`text-sm ${
                              planet.dignity_state === 'Exalted' ? 'text-green-600' :
                              planet.dignity_state === 'Debilitated' ? 'text-red-600' :
                              planet.dignity_state === 'Own' ? 'text-brand-green' :
                              'text-gray-500'
                            }`}>
                              {DIGNITY_NAMES[planet.dignity_state] || planet.dignity_state || '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'conjunctions') && (
                            <td className="text-gray-500 text-sm">
                              {planet.conjunctions?.length > 0
                                ? planet.conjunctions.map(p => PLANET_NAMES[p] || p).join(', ')
                                : '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'aspects_giving') && (
                            <td className="text-gray-500 text-sm">
                              {planet.aspects_giving_to?.length > 0 ? planet.aspects_giving_to.join(', ') : '-'}
                            </td>
                          )}
                          {isColumnVisible(planetColumns, 'aspects_receiving') && (
                            <td className="text-gray-500 text-sm">
                              {planet.aspects_receiving_from?.length > 0
                                ? planet.aspects_receiving_from.map(p => PLANET_NAMES[p] || p).join(', ')
                                : '-'}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* House Details */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-base font-medium text-gray-900">
                    Дома ({selectedVarga})
                  </h3>
                  <TableColumnSelector
                    columns={houseColumns}
                    onChange={setHouseColumns}
                  />
                </div>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr>
                        {isColumnVisible(houseColumns, 'house') && <th>Дом</th>}
                        {isColumnVisible(houseColumns, 'sign') && <th>Знак</th>}
                        {isColumnVisible(houseColumns, 'occupants') && <th>Планеты</th>}
                        {isColumnVisible(houseColumns, 'lord') && <th>Управитель</th>}
                        {isColumnVisible(houseColumns, 'aspects_received') && <th>Аспекты</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {activeChart.houses.map((house) => (
                        <tr key={house.house_number}>
                          {isColumnVisible(houseColumns, 'house') && (
                            <td className="font-medium text-gray-900">{house.house_number}</td>
                          )}
                          {isColumnVisible(houseColumns, 'sign') && (
                            <td>{SIGN_NAMES[house.sign_name] || house.sign_name}</td>
                          )}
                          {isColumnVisible(houseColumns, 'occupants') && (
                            <td className="text-gray-600">
                              {house.occupants?.length > 0
                                ? house.occupants.map(p => PLANET_NAMES[p] || p).join(', ')
                                : '-'}
                            </td>
                          )}
                          {isColumnVisible(houseColumns, 'lord') && (
                            <td className="text-gray-500">
                              {PLANET_NAMES[house.lord] || house.lord || '-'}
                            </td>
                          )}
                          {isColumnVisible(houseColumns, 'aspects_received') && (
                            <td className="text-gray-500 text-sm">
                              {house.aspects_received?.length > 0
                                ? house.aspects_received.map(p => PLANET_NAMES[p] || p).join(', ')
                                : '-'}
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Dasha & Karakas Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
              {/* Debug: Show dasha status */}
              {!digitalTwin.dasha && (
                <div className="card bg-yellow-50 border border-yellow-200">
                  <p className="text-yellow-800">Dasha data not available in response</p>
                  <p className="text-xs text-yellow-600 mt-1">Check if backend returns dasha in digital_twin</p>
                </div>
              )}
              {/* Vimshottari Dasha with expandable sub-periods */}
              {digitalTwin.dasha && (
                <div className="card">
                  <h3 className="text-base font-medium text-gray-900 mb-4">
                    Vimshottari Dasha (Периоды)
                  </h3>
                  <div className="space-y-3">
                    {/* Current Period Highlight */}
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <div className="text-sm text-blue-600 font-medium">Текущий период</div>
                      <div className="text-lg font-semibold text-blue-900 mt-1">
                        {PLANET_NAMES[digitalTwin.dasha.current_mahadasha || ''] || digitalTwin.dasha.current_mahadasha || '—'}
                        {digitalTwin.dasha.current_antardasha && (
                          <span className="text-blue-600 font-normal">
                            {' / '}
                            {PLANET_NAMES[digitalTwin.dasha.current_antardasha] || digitalTwin.dasha.current_antardasha}
                          </span>
                        )}
                        {digitalTwin.dasha.current_pratyantardasha && (
                          <span className="text-blue-500 font-normal text-sm">
                            {' / '}
                            {PLANET_NAMES[digitalTwin.dasha.current_pratyantardasha] || digitalTwin.dasha.current_pratyantardasha}
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-blue-500 mt-1">
                        Накшатра рождения: {digitalTwin.dasha.birth_nakshatra} (пада {digitalTwin.dasha.nakshatra_pada})
                      </div>
                    </div>
                    {/* Dasha Periods with expandable Antardashas */}
                    <div className="overflow-x-auto">
                      <table className="data-table text-sm">
                        <thead>
                          <tr>
                            <th className="w-8"></th>
                            <th>Период</th>
                            <th>Лет / Дней</th>
                            <th>Начало</th>
                            <th>Конец</th>
                          </tr>
                        </thead>
                        <tbody>
                          {digitalTwin.dasha.periods.slice(0, 9).map((period: DashaPeriod, idx: number) => (
                            <Fragment key={idx}>
                              {/* Mahadasha Row */}
                              <tr
                                className={`cursor-pointer hover:bg-gray-50 ${period.lord === digitalTwin.dasha?.current_mahadasha ? 'bg-blue-50' : ''}`}
                                onClick={() => {
                                  console.log('[Dasha] Clicked period:', period.lord, 'antardashas:', period.antardashas?.length);
                                  if (expandedMahadasha === period.lord) {
                                    setExpandedMahadasha(null);
                                    setExpandedAntardasha(null);
                                  } else {
                                    setExpandedMahadasha(period.lord);
                                    setExpandedAntardasha(null);
                                  }
                                }}
                              >
                                <td className="text-center">
                                  {period.antardashas && period.antardashas.length > 0 ? (
                                    <span className={`text-gray-400 transition-transform inline-block ${expandedMahadasha === period.lord ? 'rotate-90' : ''}`}>
                                      ▶
                                    </span>
                                  ) : (
                                    <span className="text-gray-300">○</span>
                                  )}
                                </td>
                                <td className={`font-medium ${period.lord === digitalTwin.dasha?.current_mahadasha ? 'text-blue-700' : 'text-gray-900'}`}>
                                  {PLANET_NAMES[period.lord] || period.lord}
                                </td>
                                <td className="text-gray-600">{period.years} лет</td>
                                <td className="text-gray-500">{period.start_date}</td>
                                <td className="text-gray-500">{period.end_date}</td>
                              </tr>
                              {/* Antardasha Rows (expanded) */}
                              {expandedMahadasha === period.lord && period.antardashas && period.antardashas.map((ad: AntardashaPeriod, adIdx: number) => (
                                <Fragment key={`${idx}-${adIdx}`}>
                                  <tr
                                    className={`cursor-pointer hover:bg-gray-50 ${
                                      period.lord === digitalTwin.dasha?.current_mahadasha &&
                                      ad.lord === digitalTwin.dasha?.current_antardasha
                                        ? 'bg-blue-100'
                                        : 'bg-gray-50'
                                    }`}
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      if (expandedAntardasha === `${period.lord}-${ad.lord}`) {
                                        setExpandedAntardasha(null);
                                      } else {
                                        setExpandedAntardasha(`${period.lord}-${ad.lord}`);
                                      }
                                    }}
                                  >
                                    <td className="text-center pl-4">
                                      {ad.pratyantardashas && ad.pratyantardashas.length > 0 && (
                                        <span className={`text-gray-300 text-xs transition-transform inline-block ${expandedAntardasha === `${period.lord}-${ad.lord}` ? 'rotate-90' : ''}`}>
                                          ▶
                                        </span>
                                      )}
                                    </td>
                                    <td className={`pl-6 ${
                                      period.lord === digitalTwin.dasha?.current_mahadasha &&
                                      ad.lord === digitalTwin.dasha?.current_antardasha
                                        ? 'text-blue-600 font-medium'
                                        : 'text-gray-600'
                                    }`}>
                                      ↳ {PLANET_NAMES[ad.lord] || ad.lord}
                                    </td>
                                    <td className="text-gray-500">{ad.days} дней</td>
                                    <td className="text-gray-400 text-xs">{ad.start_date}</td>
                                    <td className="text-gray-400 text-xs">{ad.end_date}</td>
                                  </tr>
                                  {/* Pratyantardasha Rows (expanded) */}
                                  {expandedAntardasha === `${period.lord}-${ad.lord}` && ad.pratyantardashas && ad.pratyantardashas.map((pd, pdIdx: number) => (
                                    <tr
                                      key={`${idx}-${adIdx}-${pdIdx}`}
                                      className={`${
                                        period.lord === digitalTwin.dasha?.current_mahadasha &&
                                        ad.lord === digitalTwin.dasha?.current_antardasha &&
                                        pd.lord === digitalTwin.dasha?.current_pratyantardasha
                                          ? 'bg-blue-50'
                                          : 'bg-gray-100'
                                      }`}
                                    >
                                      <td></td>
                                      <td className={`pl-12 text-xs ${
                                        period.lord === digitalTwin.dasha?.current_mahadasha &&
                                        ad.lord === digitalTwin.dasha?.current_antardasha &&
                                        pd.lord === digitalTwin.dasha?.current_pratyantardasha
                                          ? 'text-blue-500 font-medium'
                                          : 'text-gray-400'
                                      }`}>
                                        ↳↳ {PLANET_NAMES[pd.lord] || pd.lord}
                                      </td>
                                      <td className="text-gray-300 text-xs">—</td>
                                      <td className="text-gray-300 text-xs">{pd.start_date}</td>
                                      <td className="text-gray-300 text-xs">{pd.end_date}</td>
                                    </tr>
                                  ))}
                                </Fragment>
                              ))}
                            </Fragment>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="text-xs text-gray-400">
                      Нажмите на период для просмотра подпериодов (Antardasha / Pratyantardasha)
                    </div>
                  </div>
                </div>
              )}

              {/* Chara Karakas */}
              {digitalTwin.chara_karakas && (
                <div className="card">
                  <h3 className="text-base font-medium text-gray-900 mb-4">
                    Chara Karakas (Джаймини)
                  </h3>
                  <div className="space-y-3">
                    {/* Atmakaraka Highlight */}
                    <div className="bg-amber-50 p-3 rounded-lg">
                      <div className="text-sm text-amber-600 font-medium">Атмакарака (душа)</div>
                      <div className="text-lg font-semibold text-amber-900 mt-1">
                        {PLANET_NAMES[digitalTwin.chara_karakas.by_karaka['AK']] || digitalTwin.chara_karakas.by_karaka['AK'] || '—'}
                      </div>
                      <div className="text-xs text-amber-500 mt-1">
                        Даракарака (супруг): {PLANET_NAMES[digitalTwin.chara_karakas.by_karaka['DK']] || digitalTwin.chara_karakas.by_karaka['DK'] || '—'}
                      </div>
                    </div>
                    {/* Karakas Table */}
                    <div className="overflow-x-auto">
                      <table className="data-table text-sm">
                        <thead>
                          <tr>
                            <th>Карака</th>
                            <th>Планета</th>
                            <th>Градусы</th>
                            <th>Знак</th>
                          </tr>
                        </thead>
                        <tbody>
                          {digitalTwin.chara_karakas.karakas.map((karaka) => (
                            <tr key={karaka.karaka_code}>
                              <td className="font-medium text-gray-900" title={karaka.karaka_meaning}>
                                {karaka.karaka_code}
                                <span className="text-gray-400 text-xs ml-1">
                                  ({karaka.karaka_name})
                                </span>
                              </td>
                              <td className="text-gray-700">
                                {PLANET_NAMES[karaka.planet] || karaka.planet}
                              </td>
                              <td className="text-gray-500">
                                {karaka.degrees_in_sign.toFixed(2)}°
                              </td>
                              <td className="text-gray-500">
                                {SIGN_NAMES[karaka.sign] || karaka.sign}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="text-xs text-gray-400 mt-2">
                      {digitalTwin.chara_karakas.note}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Footer info */}
            <div className="mt-6 text-xs text-gray-400">
              Аянамса: {digitalTwin.meta.ayanamsa} | Delta: {digitalTwin.meta.ayanamsa_delta.toFixed(4)}°
              {detectedTimezone && (
                <> | Timezone: {detectedTimezone.timezone_name} (UTC{detectedTimezone.utc_offset >= 0 ? '+' : ''}{detectedTimezone.utc_offset})</>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
