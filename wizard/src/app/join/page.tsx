'use client';

export const dynamic = 'force-dynamic';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import DatePicker, { registerLocale } from 'react-datepicker';
import { ru } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import { useWizard } from '@/contexts/WizardContext';
import WizardProgress from '@/components/wizard/WizardProgress';
import PlaceAutocomplete from '@/components/wizard/PlaceAutocomplete';

// Register Russian locale
registerLocale('ru', ru);

type TimeAccuracy = 'exact' | 'approximate' | 'unknown';

const TIME_OPTIONS: { value: TimeAccuracy; label: string; description: string }[] = [
  { value: 'exact', label: 'Точно', description: 'Знаю время с точностью до 5 минут' },
  { value: 'approximate', label: 'Примерно', description: 'Могу ошибаться на 30-60 минут' },
  { value: 'unknown', label: 'Не знаю', description: 'Использую 12:00 (полдень)' },
];

export default function BirthDataPage() {
  const router = useRouter();
  const { state, setBirthData, setCurrentStep } = useWizard();
  const { birthData } = state;

  const [date, setDate] = useState<Date | null>(
    birthData.date ? new Date(birthData.date) : null
  );
  const [time, setTime] = useState(birthData.time || '12:00');
  const [city, setCity] = useState(birthData.city || '');
  const [lat, setLat] = useState(birthData.lat || 0);
  const [lon, setLon] = useState(birthData.lon || 0);
  const [timeAccuracy, setTimeAccuracy] = useState<TimeAccuracy>(birthData.timeAccuracy || 'exact');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePlaceSelect = (selectedCity: string, selectedLat: number, selectedLon: number) => {
    setCity(selectedCity);
    setLat(selectedLat);
    setLon(selectedLon);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!date) {
      setError('Укажите дату рождения');
      return;
    }
    if (!city || lat === 0) {
      setError('Выберите город из списка');
      return;
    }

    // Format date
    const formattedDate = date.toISOString().split('T')[0];

    // Use 12:00 if time unknown
    const finalTime = timeAccuracy === 'unknown' ? '12:00' : time;

    // Save to context
    setBirthData({
      date: formattedDate,
      time: finalTime,
      city,
      lat,
      lon,
      timeAccuracy,
      ayanamsa: 'raman',
    });

    setLoading(true);

    try {
      // Calculate chart
      const response = await fetch('https://star-meet.com/star-api/v1/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date: formattedDate,
          time: finalTime,
          lat,
          lon,
          ayanamsa: 'raman',
        }),
      });

      if (!response.ok) {
        throw new Error('Ошибка расчёта');
      }

      const data = await response.json();

      if (data.success && data.digital_twin) {
        // Store digital twin in context (will be passed via URL params or stored differently)
        // For now, we'll use sessionStorage
        sessionStorage.setItem('digitalTwin', JSON.stringify(data.digital_twin));
        sessionStorage.setItem('birthData', JSON.stringify({
          date: formattedDate,
          time: finalTime,
          city,
          lat,
          lon,
          timeAccuracy,
        }));

        // Navigate to result
        router.push('/join/result');
      } else {
        throw new Error('Неверный формат ответа');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8">
      <WizardProgress currentStep={1} totalSteps={3} />

      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Когда вы родились?
        </h1>
        <p className="text-gray-500">
          Введите данные рождения для расчёта вашей натальной карты
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Дата рождения
          </label>
          <DatePicker
            selected={date}
            onChange={(d) => setDate(d)}
            dateFormat="dd MMMM yyyy"
            locale="ru"
            showYearDropdown
            showMonthDropdown
            dropdownMode="select"
            yearDropdownItemNumber={100}
            scrollableYearDropdown
            maxDate={new Date()}
            minDate={new Date(1900, 0, 1)}
            placeholderText="Выберите дату"
            className="input-field w-full text-lg"
            wrapperClassName="w-full"
          />
        </div>

        {/* Time accuracy */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Время рождения
          </label>
          <div className="grid grid-cols-3 gap-3 mb-4">
            {TIME_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setTimeAccuracy(option.value)}
                className={`p-3 rounded-lg border-2 text-center transition-all ${
                  timeAccuracy === option.value
                    ? 'border-gray-700 bg-gray-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-gray-900">{option.label}</div>
                <div className="text-xs text-gray-500 mt-1">{option.description}</div>
              </button>
            ))}
          </div>

          {timeAccuracy !== 'unknown' && (
            <input
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              className="input-field w-full text-lg"
            />
          )}
        </div>

        {/* City */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Город рождения
          </label>
          <PlaceAutocomplete
            value={city}
            onChange={handlePlaceSelect}
            placeholder="Начните вводить название города..."
            className="text-lg"
          />
          {lat !== 0 && (
            <div className="text-xs text-gray-400 mt-1">
              Координаты: {lat.toFixed(4)}°, {lon.toFixed(4)}°
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-brand-graphite text-white font-medium py-4 px-6 rounded-xl hover:bg-brand-graphite-hover transition-colors duration-150 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Рассчитываю...
            </span>
          ) : (
            'Рассчитать карту'
          )}
        </button>
      </form>
    </div>
  );
}
