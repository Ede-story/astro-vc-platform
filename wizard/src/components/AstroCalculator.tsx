'use client';

import { useState, useEffect } from 'react';
import { fetchCalculation } from '@/lib/api';
import {
  CalculateResponse,
  InputData,
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

// Default input with RAMAN ayanamsa
const DEFAULT_INPUT: InputData = {
  date: '1982-05-30',
  time: '09:45',
  city: 'Санкт-Петербург',
  lat: 59.93,
  lon: 30.33,
  timezone: 3,
  ayanamsa: 'raman',
};

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

    setSaveStatus('saving');
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'https://star-meet.com/star-api'}/v1/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          input_data: input,
          chart_data: result,
        }),
      });

      if (response.ok) {
        setSaveStatus('saved');
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

        {/* Collapsed Form Summary */}
        {isFormCollapsed && result && (
          <div className="card mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="text-sm">
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
              <div>
                <label className="input-label">Дата</label>
                <input
                  type="date"
                  className="input-field"
                  value={input.date}
                  onChange={(e) => setInput({ ...input, date: e.target.value })}
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

              <div>
                <label className="input-label">Город</label>
                <input
                  type="text"
                  className="input-field"
                  value={input.city}
                  onChange={(e) => setInput({ ...input, city: e.target.value })}
                />
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
