'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';

interface Profile {
  id: string;
  name: string;
  username: string;
  avatar_url: string | null;
  birth_city: string | null;
  digital_twin: any;
  seeking: string[] | null;
  career: string | null;
}

const getZodiacEmoji = (sign: string): string => {
  const zodiacEmojis: Record<string, string> = {
    'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
    'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
    'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
  };
  return zodiacEmojis[sign] || '⭐';
};

const getSunSign = (digitalTwin: any): string | null => {
  if (!digitalTwin?.vargas?.D1?.planets) return null;
  const planets = digitalTwin.vargas.D1.planets;
  const sun = planets.find((p: any) => p.name === 'Sun');
  return sun?.sign_name || null;
};

const SEEKING_LABELS: Record<string, string> = {
  'business': 'Бизнес',
  'mentor': 'Ментор',
  'romance': 'Романтика',
  'friendship': 'Дружба',
  'networking': 'Нетворкинг',
  'collaboration': 'Коллаборация',
};

export default function ExploreClient() {
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const supabase = createClient();

  useEffect(() => {
    async function fetchProfiles() {
      const { data: { user } } = await supabase.auth.getUser();

      let query = supabase
        .from('profiles')
        .select('id, name, username, avatar_url, birth_city, digital_twin, seeking, career')
        .eq('is_public', true)
        .eq('onboarding_completed', true)
        .limit(50);

      if (user) {
        query = query.neq('user_id', user.id);
      }

      const { data, error } = await query;

      if (error) {
        console.error('Error fetching profiles:', error);
      } else {
        setProfiles(data || []);
      }
      setLoading(false);
    }

    fetchProfiles();
  }, [supabase]);

  const filteredProfiles = profiles.filter(profile => {
    if (filter === 'all') return true;
    return profile.seeking?.includes(filter);
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b px-6 py-4 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-semibold">StarMeet</Link>
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700">
            Мой профиль
          </Link>
        </div>
      </header>

      <div className="bg-white border-b px-6 py-3">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors ${
                filter === 'all'
                  ? 'bg-brand-graphite text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Все
            </button>
            {Object.entries(SEEKING_LABELS).map(([key, label]) => (
              <button
                key={key}
                onClick={() => setFilter(key)}
                className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors ${
                  filter === key
                    ? 'bg-brand-graphite text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto px-6 py-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">
          Найти людей
        </h1>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
            <p className="text-gray-500 mt-4">Загрузка...</p>
          </div>
        ) : filteredProfiles.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl">
            <p className="text-gray-500">Пока нет пользователей</p>
            <p className="text-gray-400 text-sm mt-2">Станьте первым!</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {filteredProfiles.map((profile) => {
              const sunSign = getSunSign(profile.digital_twin);

              return (
                <Link
                  key={profile.id}
                  href={`/profile/${profile.username}`}
                  className="bg-white rounded-xl p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                      {profile.avatar_url ? (
                        <img
                          src={profile.avatar_url}
                          alt={profile.name}
                          className="w-14 h-14 rounded-full object-cover"
                        />
                      ) : (
                        <span className="text-2xl">👤</span>
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <h2 className="font-semibold text-gray-900 truncate">
                          {profile.name}
                        </h2>
                        {sunSign && (
                          <span className="text-lg" title={sunSign}>
                            {getZodiacEmoji(sunSign)}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-500 text-sm">@{profile.username}</p>

                      {profile.birth_city && (
                        <p className="text-gray-400 text-sm mt-1">
                          📍 {profile.birth_city}
                        </p>
                      )}

                      {profile.career && (
                        <p className="text-gray-600 text-sm mt-2 truncate">
                          {profile.career.split('\n')[0]}
                        </p>
                      )}

                      {profile.seeking && profile.seeking.length > 0 && (
                        <div className="flex gap-1 mt-2 flex-wrap">
                          {profile.seeking.slice(0, 2).map((item) => (
                            <span
                              key={item}
                              className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded text-xs"
                            >
                              {SEEKING_LABELS[item] || item}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <span className="text-gray-300">→</span>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
