'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';
import { User } from '@supabase/supabase-js';

interface Profile {
  id: string;
  name: string;
  username: string | null;
  birth_date: string;
  birth_city: string;
  ayanamsa: string;
  is_primary: boolean;
  created_at: string;
}

export default function DashboardClient() {
  const [user, setUser] = useState<User | null>(null);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
        return;
      }
      setUser(user);
      await loadProfiles(user.id);
      setLoading(false);
    };

    getUser();
  }, []);

  const loadProfiles = async (userId: string) => {
    const { data, error } = await supabase
      .from('profiles')
      .select('id, name, username, birth_date, birth_city, ayanamsa, is_primary, created_at')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });

    if (data) {
      setProfiles(data);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/login');
    router.refresh();
  };

  const deleteProfile = async (profileId: string) => {
    if (!confirm('Удалить этот профиль?')) return;

    const { error } = await supabase
      .from('profiles')
      .delete()
      .eq('id', profileId);

    if (!error && user) {
      await loadProfiles(user.id);
    }
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">
              StarMeet
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              {user?.email}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/join"
              className="text-white font-medium py-2 px-4 rounded-md transition-colors duration-150 text-sm"
              style={{ backgroundColor: '#2f3538' }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3d4448'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2f3538'}
            >
              + Новый расчет
            </Link>
            <button
              onClick={handleLogout}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Выйти
            </button>
          </div>
        </header>

        {/* Profiles */}
        <div className="card">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Мои профили
          </h2>

          {profiles.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500 mb-4">
                У вас пока нет сохраненных профилей
              </p>
              <Link
                href="/join"
                className="text-brand-green hover:text-brand-green-hover"
              >
                Создать первый профиль
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {profiles.map((profile) => (
                <div
                  key={profile.id}
                  className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">
                        {profile.name}
                      </span>
                      {profile.is_primary && (
                        <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                          Основной
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                      {formatDate(profile.birth_date)} | {profile.birth_city || 'Город не указан'} | {profile.ayanamsa}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Link
                      href={`/join?profile=${profile.id}`}
                      className="text-sm text-brand-green hover:text-brand-green-hover"
                    >
                      Открыть
                    </Link>
                    <button
                      onClick={() => deleteProfile(profile.id)}
                      className="text-sm text-red-500 hover:text-red-600"
                    >
                      Удалить
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex gap-4 mt-6">
          <Link
            href="/explore"
            className="flex-1 py-3 text-white rounded-xl font-medium transition-colors text-center"
            style={{ backgroundColor: '#B5C76E' }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#A4B85D'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#B5C76E'}
          >
            🔍 Найти людей
          </Link>
          {profiles.length > 0 && profiles[0].username && (
            <Link
              href={`/profile/${profiles[0].username}`}
              className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors text-center"
            >
              👤 Мой профиль
            </Link>
          )}
        </div>

        {/* Vedic Astrology Calculator Link */}
        <div className="mt-4">
          <Link
            href="/join"
            className="block w-full py-3 text-white rounded-xl font-medium transition-colors text-center"
            style={{ backgroundColor: '#2f3538' }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3d4448'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#2f3538'}
          >
            ⭐ Ведическая астрология
          </Link>
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {profiles.length}
            </div>
            <div className="text-sm text-gray-500">Профилей</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-semibold text-gray-900">
              0
            </div>
            <div className="text-sm text-gray-500">Совпадений</div>
          </div>
          <div className="card text-center">
            <div className="text-2xl font-semibold text-gray-900">
              0
            </div>
            <div className="text-sm text-gray-500">Сообщений</div>
          </div>
        </div>
      </div>
    </div>
  );
}
