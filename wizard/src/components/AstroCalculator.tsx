'use client';

import { useState, useEffect } from 'react';
import { fetchCalculation } from '@/lib/api';
import {
  CalculateResponse,
  InputData,
  VARGA_LIST,
  SIGN_NAMES,
  PLANET_NAMES,
  SIGN_LORDS
} from '@/types/astro';

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

  // Get planet sign for selected varga
  const getPlanetVargaSign = (planet: CalculateResponse['planets'][0]) => {
    if (selectedVarga === 'D1') {
      return planet.sign;
    }
    // Use varga_data from API response for non-D1 vargas
    if (result?.varga_data?.planets) {
      return result.varga_data.planets[planet.name] || planet.sign;
    }
    // Fallback to varga_signs from planet data
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

    // For other vargas, calculate based on varga ascendant
    if (result.varga_data) {
      const vargaAsc = result.varga_data.ascendant;
      const signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'];
      const ascIdx = signs.indexOf(vargaAsc);
      if (ascIdx === -1) return [];
      const houseSign = signs[(ascIdx + houseNum - 1) % 12];

      return Object.entries(result.varga_data.planets)
        .filter(([_, sign]) => sign === houseSign)
        .map(([planet, _]) => PLANET_NAMES[planet] || planet);
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

    // For other vargas, calculate from varga ascendant
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

        {/* Input Form */}
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
                <h3 className="text-base font-medium text-gray-900 mb-4">
                  Планеты ({selectedVarga})
                </h3>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Планета</th>
                        <th>Знак</th>
                        <th>Накшатра</th>
                        <th>Дом</th>
                        <th>Управитель</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.planets.map((planet) => {
                        const vargaSign = getPlanetVargaSign(planet);
                        return (
                          <tr key={planet.name}>
                            <td className="font-medium text-gray-900">
                              {PLANET_NAMES[planet.name] || planet.name}
                            </td>
                            <td>
                              {SIGN_NAMES[vargaSign] || vargaSign}
                              {selectedVarga === 'D1' && (
                                <span className="text-gray-400 ml-1 text-xs">
                                  {planet.degrees.toFixed(1)}°
                                </span>
                              )}
                            </td>
                            <td className="text-gray-600">
                              {planet.nakshatra}
                              <span className="text-gray-400 ml-1">
                                ({planet.nakshatra_pada})
                              </span>
                            </td>
                            <td>{planet.house}</td>
                            <td className="text-gray-500">
                              {PLANET_NAMES[SIGN_LORDS[vargaSign]] || SIGN_LORDS[vargaSign]}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* House Details */}
              <div className="card">
                <h3 className="text-base font-medium text-gray-900 mb-4">
                  Дома ({selectedVarga})
                </h3>
                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Дом</th>
                        <th>Знак</th>
                        <th>Планеты</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((houseNum) => {
                        const sign = getHouseSign(houseNum);
                        const planets = getPlanetsInHouse(houseNum);
                        return (
                          <tr key={houseNum}>
                            <td className="font-medium text-gray-900">{houseNum}</td>
                            <td>{SIGN_NAMES[sign] || sign}</td>
                            <td className="text-gray-600">
                              {planets.length > 0 ? planets.join(', ') : '-'}
                            </td>
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
