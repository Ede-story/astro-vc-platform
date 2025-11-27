'use client';

import { useState, useEffect, useRef } from 'react';
import { fetchCalculation } from '@/lib/api';
import DatePicker, { registerLocale } from 'react-datepicker';
import { ru } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import {
  CalculateResponse,
  InputData,
  SavedProfile,
  VARGA_LIST,
  SIGN_NAMES,
  PLANET_NAMES,
  SIGN_LORDS,
  DIGNITY_NAMES
} from '@/types/astro';
import TableColumnSelector, {
  ColumnConfig,
  DEFAULT_PLANET_COLUMNS,
  DEFAULT_HOUSE_COLUMNS
} from './TableColumnSelector';

// Register Russian locale for date picker
registerLocale('ru', ru);

// Default input with RAMAN ayanamsa
const DEFAULT_INPUT: InputData = {
  name: '',
  date: '1982-05-30',
  time: '09:45',
  city: 'Санкт-Петербург',
  lat: 59.93,
  lon: 30.33,
  timezone: 3,
  ayanamsa: 'raman',
};

const API_URL = 'https://star-meet.com/star-api';

export default function AstroCalculator() {
  const [input, setInput] = useState<InputData>(DEFAULT_INPUT);
  const [selectedVarga, setSelectedVarga] = useState('D1');
  const [result, setResult] = useState<CalculateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  // Collapsible form state
  const [isFormCollapsed, setIsFormCollapsed] = useState(false);

  // Column visibility state
  const [planetColumns, setPlanetColumns] = useState<ColumnConfig[]>(DEFAULT_PLANET_COLUMNS);
  const [houseColumns, setHouseColumns] = useState<ColumnConfig[]>(DEFAULT_HOUSE_COLUMNS);

  // Saved profiles state
  const [savedProfiles, setSavedProfiles] = useState<SavedProfile[]>([]);
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [profilesLoading, setProfilesLoading] = useState(false);

  // City search state
  const [citySuggestions, setCitySuggestions] = useState<Array<{
    display_name: string;
    lat: string;
    lon: string;
  }>>([]);
  const [citySearchLoading, setCitySearchLoading] = useState(false);
  const [showCitySuggestions, setShowCitySuggestions] = useState(false);
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

  // Search city coordinates using Nominatim API
  const searchCity = async (query: string) => {
    if (query.length < 2) {
      setCitySuggestions([]);
      return;
    }

    setCitySearchLoading(true);
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&accept-language=ru`,
        { headers: { 'User-Agent': 'StarMeet/1.0' } }
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
    const timeoutId = setTimeout(() => {
      if (input.city && input.city.length >= 2) {
        searchCity(input.city);
      }
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [input.city]);

  // Select city from suggestions
  const selectCity = (suggestion: { display_name: string; lat: string; lon: string }) => {
    // Extract just city name (first part before comma)
    const cityName = suggestion.display_name.split(',')[0].trim();
    setInput({
      ...input,
      city: cityName,
      lat: parseFloat(suggestion.lat),
      lon: parseFloat(suggestion.lon),
    });
    setShowCitySuggestions(false);
    setCitySuggestions([]);
  };

  // Load profiles on mount
  useEffect(() => {
    loadProfiles();
  }, []);

  const loadProfiles = async () => {
    setProfilesLoading(true);
    try {
      const response = await fetch(`${API_URL}/v1/profiles`);
      if (response.ok) {
        const data = await response.json();
        setSavedProfiles(data.profiles || []);
      }
    } catch (err) {
      console.error('Failed to load profiles:', err);
    } finally {
      setProfilesLoading(false);
    }
  };

  const loadProfile = async (profileId: string) => {
    try {
      const response = await fetch(`${API_URL}/v1/profiles/${profileId}`);
      if (response.ok) {
        const data = await response.json();
        // Load input data from profile
        if (data.input) {
          setInput({
            name: data.input.name || '',
            date: data.input.date || DEFAULT_INPUT.date,
            time: data.input.time || DEFAULT_INPUT.time,
            city: data.input.city || DEFAULT_INPUT.city,
            lat: data.input.lat || DEFAULT_INPUT.lat,
            lon: data.input.lon || DEFAULT_INPUT.lon,
            timezone: data.input.timezone || DEFAULT_INPUT.timezone,
            ayanamsa: data.input.ayanamsa || DEFAULT_INPUT.ayanamsa,
          });
        }
        // Load chart data if available
        if (data.chart) {
          setResult(data.chart);
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
      const response = await fetch(`${API_URL}/v1/profiles/${profileId}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setSavedProfiles((prev: SavedProfile[]) => prev.filter((p: SavedProfile) => p.id !== profileId));
        if (activeProfileId === profileId) {
          setActiveProfileId(null);
        }
      }
    } catch (err) {
      console.error('Failed to delete profile:', err);
    }
  };

  // Re-fetch when varga changes (to get updated varga_data)
  useEffect(() => {
    if (result) {
      handleCalculate();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedVarga]);

  const handleCalculate = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetchCalculation({
        date: input.date,
        time: input.time,
        lat: input.lat,
        lon: input.lon,
        timezone: input.timezone,
        ayanamsa: input.ayanamsa,
        varga: selectedVarga,
      });
      setResult(response);
      // Collapse form after successful calculation
      setIsFormCollapsed(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка расчета');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!result) return;
    if (!input.name.trim()) {
      alert('Введите имя профиля');
      return;
    }

    setSaveStatus('saving');
    try {
      const response = await fetch(`${API_URL}/v1/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_data: input,
          chart_data: result,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSaveStatus('saved');
        setActiveProfileId(data.profile_id);
        // Reload profiles list
        await loadProfiles();
        setTimeout(() => setSaveStatus(null), 3000);
      } else {
        setSaveStatus('error');
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

  // Get planet sign for selected varga
  const getPlanetVargaSign = (planet: CalculateResponse['planets'][0]) => {
    if (selectedVarga === 'D1') {
      return planet.sign;
    }
    if (result?.varga_data?.planets) {
      return result.varga_data.planets[planet.name] || planet.sign;
    }
    return planet.varga_signs[selectedVarga as keyof typeof planet.varga_signs] || planet.sign;
  };

  // Get planets in a specific house for the selected varga
  const getPlanetsInHouse = (houseNum: number): string[] => {
    if (!result) return [];

    if (selectedVarga === 'D1') {
      return result.planets
        .filter(p => p.house === houseNum)
        .map(p => PLANET_NAMES[p.name] || p.name);
    }

    if (result.varga_data) {
      const vargaAsc = result.varga_data.ascendant;
      const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
      const ascIdx = signs.indexOf(vargaAsc);
      if (ascIdx === -1) return [];
      const houseSign = signs[(ascIdx + houseNum - 1) % 12];

      return Object.entries(result.varga_data.planets)
        .filter(([, sign]) => sign === houseSign)
        .map(([planet]) => PLANET_NAMES[planet] || planet);
    }

    return [];
  };

  // Get house sign for selected varga
  const getHouseSign = (houseNum: number): string => {
    if (!result) return '';

    if (selectedVarga === 'D1') {
      const house = result.houses.find(h => h.house === houseNum);
      return house?.sign || '';
    }

    if (result.varga_data) {
      const vargaAsc = result.varga_data.ascendant;
      const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
      const ascIdx = signs.indexOf(vargaAsc);
      if (ascIdx === -1) return '';
      return signs[(ascIdx + houseNum - 1) % 12];
    }

    return '';
  };

  // Get current ascendant based on selected varga
  const getCurrentAscendant = (): string => {
    if (!result) return '';

    if (selectedVarga === 'D1') {
      const sign = SIGN_NAMES[result.ascendant.sign] || result.ascendant.sign;
      return `${sign} ${result.ascendant.degrees.toFixed(2)}°`;
    }

    if (result.varga_data?.ascendant) {
      return SIGN_NAMES[result.varga_data.ascendant] || result.varga_data.ascendant;
    }

    return '';
  };

  // Check if column is visible
  const isColumnVisible = (columns: ColumnConfig[], id: string): boolean => {
    return columns.find(c => c.id === id)?.enabled ?? false;
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-2xl font-semibold text-gray-900">
            StarMeet
          </h1>
          <p className="text-gray-500 text-sm mt-1">Ведический астрологический калькулятор</p>
        </header>

        {/* Saved Profiles Dropdown */}
        <div className="card mb-6">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 flex-1">
              <label className="text-sm font-medium text-gray-700 whitespace-nowrap">Профиль:</label>
              <select
                className="input-field flex-1"
                value={activeProfileId || ''}
                onChange={(e) => {
                  const value = e.target.value;
                  if (value === '') {
                    // "Новый" selected
                    setInput({ ...DEFAULT_INPUT, name: '' });
                    setResult(null);
                    setActiveProfileId(null);
                    setIsFormCollapsed(false);
                  } else {
                    loadProfile(value);
                  }
                }}
              >
                <option value="">+ Новый профиль</option>
                {savedProfiles.filter((p: SavedProfile) => p.name && p.name.trim() !== '').map((profile: SavedProfile) => (
                  <option key={profile.id} value={profile.id}>
                    {profile.name}
                  </option>
                ))}
              </select>
            </div>
            {activeProfileId && (
              <button
                onClick={() => deleteProfile(activeProfileId)}
                className="text-sm text-red-500 hover:text-red-700 flex items-center gap-1"
                title="Удалить профиль"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
                Удалить
              </button>
            )}
          </div>
        </div>

        {/* Collapsed Form Summary */}
        {isFormCollapsed && result && (
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
                </div>
              </div>
              <button
                onClick={() => setIsFormCollapsed(false)}
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
                  onChange={(e) => setInput({ ...input, city: e.target.value })}
                  onFocus={() => citySuggestions.length > 0 && setShowCitySuggestions(true)}
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
                  <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {citySuggestions.map((suggestion, index) => (
                      <button
                        key={index}
                        type="button"
                        className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 border-b border-gray-100 last:border-0"
                        onClick={() => selectCity(suggestion)}
                      >
                        {suggestion.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="input-label">Часовой пояс</label>
                <input
                  type="number"
                  className="input-field"
                  value={input.timezone}
                  onChange={(e) => setInput({ ...input, timezone: parseFloat(e.target.value) })}
                  step="0.5"
                />
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
                  className="btn-primary flex-1 disabled:opacity-50"
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
        {result && (
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
                      {result.planets.map((planet) => {
                        const vargaSign = getPlanetVargaSign(planet);
                        return (
                          <tr key={planet.name}>
                            {isColumnVisible(planetColumns, 'name') && (
                              <td className="font-medium text-gray-900">
                                {PLANET_NAMES[planet.name] || planet.name}
                              </td>
                            )}
                            {isColumnVisible(planetColumns, 'sign') && (
                              <td>
                                {SIGN_NAMES[vargaSign] || vargaSign}
                                {selectedVarga === 'D1' && (
                                  <span className="text-gray-400 ml-1 text-xs">
                                    {planet.degrees.toFixed(1)}°
                                  </span>
                                )}
                              </td>
                            )}
                            {isColumnVisible(planetColumns, 'nakshatra') && (
                              <td className="text-gray-600">
                                {planet.nakshatra}
                                <span className="text-gray-400 ml-1">
                                  ({planet.nakshatra_pada})
                                </span>
                              </td>
                            )}
                            {isColumnVisible(planetColumns, 'house') && (
                              <td>{planet.house}</td>
                            )}
                            {isColumnVisible(planetColumns, 'sign_lord') && (
                              <td className="text-gray-500">
                                {PLANET_NAMES[SIGN_LORDS[vargaSign]] || SIGN_LORDS[vargaSign] || '-'}
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
                                planet.dignity === 'Exalted' ? 'text-green-600' :
                                planet.dignity === 'Debilitated' ? 'text-red-600' :
                                planet.dignity === 'Own' ? 'text-blue-600' :
                                'text-gray-500'
                              }`}>
                                {DIGNITY_NAMES[planet.dignity] || planet.dignity || '-'}
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
                                {planet.aspects_giving?.length > 0 ? planet.aspects_giving.join(', ') : '-'}
                              </td>
                            )}
                            {isColumnVisible(planetColumns, 'aspects_receiving') && (
                              <td className="text-gray-500 text-sm">
                                {planet.aspects_receiving?.length > 0
                                  ? planet.aspects_receiving.map(p => PLANET_NAMES[p] || p).join(', ')
                                  : '-'}
                              </td>
                            )}
                          </tr>
                        );
                      })}
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
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
                        const sign = getHouseSign(houseNum);
                        const planets = getPlanetsInHouse(houseNum);
                        const houseData = result.houses.find(h => h.house === houseNum);
                        return (
                          <tr key={houseNum}>
                            {isColumnVisible(houseColumns, 'house') && (
                              <td className="font-medium text-gray-900">{houseNum}</td>
                            )}
                            {isColumnVisible(houseColumns, 'sign') && (
                              <td>{SIGN_NAMES[sign] || sign}</td>
                            )}
                            {isColumnVisible(houseColumns, 'occupants') && (
                              <td className="text-gray-600">
                                {planets.length > 0 ? planets.join(', ') : '-'}
                              </td>
                            )}
                            {isColumnVisible(houseColumns, 'lord') && (
                              <td className="text-gray-500">
                                {PLANET_NAMES[SIGN_LORDS[sign]] || SIGN_LORDS[sign] || '-'}
                              </td>
                            )}
                            {isColumnVisible(houseColumns, 'aspects_received') && (
                              <td className="text-gray-500 text-sm">
                                {(houseData?.aspects_received?.length ?? 0) > 0
                                  ? houseData!.aspects_received.map((p: string) => PLANET_NAMES[p] || p).join(', ')
                                  : '-'}
                              </td>
                            )}
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Footer info */}
            <div className="mt-6 text-xs text-gray-400">
              Аянамса: {result.ayanamsa} | Варга: {result.requested_varga || 'D1'}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
