export const dynamic = 'force-dynamic';

import { createClient } from '@/lib/supabase/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';

interface PageProps {
  params: { username: string };
}

// Helper to get zodiac emoji
const getZodiacEmoji = (sign: string): string => {
  const zodiacEmojis: Record<string, string> = {
    'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
    'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
    'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
  };
  return zodiacEmojis[sign] || '⭐';
};

// Helper to get signs from digital_twin
const getSignsFromChart = (digitalTwin: any) => {
  if (!digitalTwin?.vargas?.D1) return null;

  const d1 = digitalTwin.vargas.D1;
  const planets = d1.planets || [];

  // Find Sun sign from planets array
  const sun = planets.find((p: any) => p.name === 'Sun');
  const sunSign = sun?.sign_name || null;

  // Find Moon sign
  const moon = planets.find((p: any) => p.name === 'Moon');
  const moonSign = moon?.sign_name || null;

  // Find Ascendant
  const ascendant = d1.ascendant?.sign_name || null;

  return { sunSign, moonSign, ascendant };
};

// Mapping for seeking options display
const SEEKING_LABELS: Record<string, string> = {
  'business': 'Бизнес-партнёр',
  'mentor': 'Ментор',
  'romance': 'Романтика',
  'friendship': 'Дружба',
  'networking': 'Нетворкинг',
  'collaboration': 'Коллаборация',
};

const OFFERING_LABELS: Record<string, string> = {
  'expertise': 'Экспертиза',
  'investment': 'Инвестиции',
  'mentoring': 'Менторство',
  'connections': 'Связи',
  'creativity': 'Креатив',
  'support': 'Поддержка',
};

export default async function ProfilePage({ params }: PageProps) {
  const supabase = await createClient();

  // Fetch profile by username
  const { data: profile, error } = await supabase
    .from('profiles')
    .select('*')
    .eq('username', params.username)
    .single();

  if (error || !profile) {
    notFound();
  }

  // Check if profile is public or belongs to current user
  const { data: { user } } = await supabase.auth.getUser();
  const isOwner = user?.id === profile.user_id;

  if (!profile.is_public && !isOwner) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-gray-900">Профиль скрыт</h1>
          <p className="text-gray-500 mt-2">Этот пользователь скрыл свой профиль</p>
          <Link href="/explore" className="text-brand-green-hover mt-4 inline-block">
            ← Вернуться к поиску
          </Link>
        </div>
      </div>
    );
  }

  // Extract astrological data
  const signs = getSignsFromChart(profile.digital_twin);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b px-6 py-4">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <Link href="/explore" className="text-gray-500 hover:text-gray-700">
            ← Назад
          </Link>
          <Link href="/" className="text-xl font-semibold">StarMeet</Link>
          <div className="w-16" /> {/* Spacer */}
        </div>
      </header>

      {/* Profile Content */}
      <main className="max-w-2xl mx-auto px-6 py-8">
        <div className="bg-white rounded-2xl p-8 shadow-sm">
          {/* Avatar & Name */}
          <div className="text-center mb-6">
            <div className="w-24 h-24 mx-auto bg-gray-100 rounded-full flex items-center justify-center mb-4">
              {profile.avatar_url ? (
                <img
                  src={profile.avatar_url}
                  alt={profile.name}
                  className="w-24 h-24 rounded-full object-cover"
                />
              ) : (
                <span className="text-4xl">👤</span>
              )}
            </div>
            <h1 className="text-2xl font-semibold text-gray-900">{profile.name}</h1>
            <p className="text-gray-500">@{profile.username}</p>
          </div>

          {/* Zodiac Signs */}
          {signs && (
            <div className="flex justify-center gap-4 mb-6">
              {signs.sunSign && (
                <div className="text-center px-4 py-2 bg-amber-50 rounded-xl">
                  <span className="text-2xl">{getZodiacEmoji(signs.sunSign)}</span>
                  <p className="text-xs text-gray-500 mt-1">☀️ {signs.sunSign}</p>
                </div>
              )}
              {signs.moonSign && (
                <div className="text-center px-4 py-2 bg-blue-50 rounded-xl">
                  <span className="text-2xl">{getZodiacEmoji(signs.moonSign)}</span>
                  <p className="text-xs text-gray-500 mt-1">🌙 {signs.moonSign}</p>
                </div>
              )}
              {signs.ascendant && (
                <div className="text-center px-4 py-2 bg-purple-50 rounded-xl">
                  <span className="text-2xl">{getZodiacEmoji(signs.ascendant)}</span>
                  <p className="text-xs text-gray-500 mt-1">⬆️ {signs.ascendant}</p>
                </div>
              )}
            </div>
          )}

          {/* Location */}
          {profile.birth_city && (
            <p className="text-center text-gray-500 mb-6">
              📍 {profile.birth_city}
            </p>
          )}

          {/* Career */}
          {profile.career && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-gray-500 mb-2">Карьера</h2>
              <p className="text-gray-900 whitespace-pre-line">{profile.career}</p>
            </div>
          )}

          {/* Bio */}
          {profile.bio && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-gray-500 mb-2">О себе</h2>
              <p className="text-gray-900 whitespace-pre-line">{profile.bio}</p>
            </div>
          )}

          {/* Seeking */}
          {profile.seeking && profile.seeking.length > 0 && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-gray-500 mb-2">Ищет</h2>
              <div className="flex flex-wrap gap-2">
                {profile.seeking.map((item: string) => (
                  <span
                    key={item}
                    className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                  >
                    {SEEKING_LABELS[item] || item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Offerings */}
          {profile.offerings && profile.offerings.length > 0 && (
            <div className="mb-6">
              <h2 className="text-sm font-medium text-gray-500 mb-2">Предлагает</h2>
              <div className="flex flex-wrap gap-2">
                {profile.offerings.map((item: string) => (
                  <span
                    key={item}
                    className="px-3 py-1 bg-green-50 text-green-700 rounded-full text-sm"
                  >
                    {OFFERING_LABELS[item] || item}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Message Button (if not owner) */}
          {!isOwner && (
            <button className="w-full py-3 bg-brand-graphite text-white rounded-xl font-medium hover:bg-brand-graphite-hover transition-colors mt-6">
              💬 Написать сообщение
            </button>
          )}

          {/* Edit Button (if owner) */}
          {isOwner && (
            <Link
              href="/dashboard"
              className="block w-full py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors mt-6 text-center"
            >
              ✏️ Редактировать профиль
            </Link>
          )}

          {/* Vedic Astrology Calculator Link */}
          <Link
            href="/join"
            className="block w-full py-3 bg-brand-graphite text-white rounded-xl font-medium hover:bg-brand-graphite-hover transition-colors mt-4 text-center"
          >
            ⭐ Ведическая астрология
          </Link>
        </div>
      </main>
    </div>
  );
}
