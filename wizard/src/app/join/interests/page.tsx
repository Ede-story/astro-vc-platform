'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import WizardProgress from '@/components/wizard/WizardProgress';
import InterestSelector from '@/components/wizard/InterestSelector';
import { createClient } from '@/lib/supabase/client';
import { useAuth } from '@/hooks/useAuth';

const SEEKING_OPTIONS = [
  { id: 'business', label: 'Бизнес-партнёр', icon: '💼' },
  { id: 'mentor', label: 'Ментор', icon: '🎓' },
  { id: 'romance', label: 'Романтика', icon: '💕' },
  { id: 'friendship', label: 'Дружба', icon: '🤝' },
  { id: 'networking', label: 'Нетворкинг', icon: '🌐' },
  { id: 'collaboration', label: 'Коллаборация', icon: '🎯' },
];

const OFFERING_OPTIONS = [
  { id: 'expertise', label: 'Экспертиза', icon: '💡' },
  { id: 'investment', label: 'Инвестиции', icon: '💰' },
  { id: 'mentoring', label: 'Менторство', icon: '📚' },
  { id: 'connections', label: 'Связи', icon: '🔗' },
  { id: 'creativity', label: 'Креатив', icon: '🎨' },
  { id: 'support', label: 'Поддержка', icon: '🤗' },
];

export default function InterestsPage() {
  const router = useRouter();
  const supabase = createClient();
  const { user, isAuthenticated } = useAuth();

  const [seeking, setSeeking] = useState<string[]>([]);
  const [offerings, setOfferings] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Check if we have required data
  useEffect(() => {
    const birthData = sessionStorage.getItem('birthData');
    const digitalTwin = sessionStorage.getItem('digitalTwin');
    if (!birthData || !digitalTwin) {
      router.push('/join');
    }
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (seeking.length === 0) {
      setError('Выберите хотя бы одну цель');
      return;
    }

    setLoading(true);

    try {
      // Get all data from sessionStorage
      const birthDataStr = sessionStorage.getItem('birthData');
      const digitalTwinStr = sessionStorage.getItem('digitalTwin');
      const profileDataStr = sessionStorage.getItem('profileData');
      const psychScoresStr = sessionStorage.getItem('psychScores');

      if (!birthDataStr || !digitalTwinStr) {
        throw new Error('Данные потеряны. Начните заново.');
      }

      const birthData = JSON.parse(birthDataStr);
      const digitalTwin = JSON.parse(digitalTwinStr);
      const profileData = profileDataStr ? JSON.parse(profileDataStr) : {};
      const psychScores = psychScoresStr ? JSON.parse(psychScoresStr) : null;

      // Check auth - if not logged in, redirect to signup with data
      if (!isAuthenticated || !user) {
        // Store interests before redirecting
        sessionStorage.setItem('interestsData', JSON.stringify({ seeking, offerings }));
        router.push('/signup?redirect=/join/complete');
        return;
      }

      // Save profile to database
      const { data, error: dbError } = await supabase
        .from('profiles')
        .insert({
          user_id: user.id,
          name: profileData.fullName || 'Пользователь',
          username: profileData.username || null,
          bio: profileData.bio || null,
          career: profileData.career || null,
          birth_date: birthData.date,
          birth_time: birthData.time,
          birth_city: birthData.city,
          birth_latitude: birthData.lat,
          birth_longitude: birthData.lon,
          birth_timezone: birthData.timezone || 0,
          ayanamsa: birthData.ayanamsa || 'raman',
          digital_twin: digitalTwin,
          psych_scores: psychScores,
          psych_completed_at: psychScores ? new Date().toISOString() : null,
          seeking: seeking,
          offerings: offerings,
          is_primary: true,
          onboarding_completed: true,
        })
        .select()
        .single();

      if (dbError) {
        throw new Error(dbError.message);
      }

      // Clear sessionStorage
      sessionStorage.removeItem('birthData');
      sessionStorage.removeItem('digitalTwin');
      sessionStorage.removeItem('profileData');
      sessionStorage.removeItem('psychScores');
      sessionStorage.removeItem('interestsData');

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8">
      <WizardProgress currentStep={4} totalSteps={4} />

      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Что вы ищете?
        </h1>
        <p className="text-gray-500">
          Это поможет нам находить релевантные совпадения
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Seeking */}
        <InterestSelector
          title="Я ищу"
          options={SEEKING_OPTIONS}
          selected={seeking}
          onChange={setSeeking}
        />

        {/* Offerings */}
        <InterestSelector
          title="Я предлагаю"
          options={OFFERING_OPTIONS}
          selected={offerings}
          onChange={setOfferings}
        />

        {/* Error */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Auth hint */}
        {!isAuthenticated && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700 text-sm">
            Для сохранения профиля потребуется создать аккаунт
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
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Сохранение...
            </span>
          ) : isAuthenticated ? (
            'Завершить'
          ) : (
            'Создать аккаунт'
          )}
        </button>
      </form>
    </div>
  );
}
