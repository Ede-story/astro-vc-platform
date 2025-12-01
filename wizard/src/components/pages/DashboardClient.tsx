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
  const [primaryProfile, setPrimaryProfile] = useState<Profile | null>(null);
  const [friendProfiles, setFriendProfiles] = useState<Profile[]>([]);
  const [showFriends, setShowFriends] = useState(true);
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
      const primary = data.find(p => p.is_primary) || null;
      const friends = data.filter(p => !p.is_primary);
      setPrimaryProfile(primary);
      setFriendProfiles(friends);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push('/login');
    router.refresh();
  };

  const deleteProfile = async (profileId: string, isPrimary: boolean) => {
    const confirmMsg = isPrimary
      ? 'Удалить ваш основной профиль? Это действие нельзя отменить.'
      : 'Удалить этот профиль?';
    if (!confirm(confirmMsg)) return;

    const { error } = await supabase
      .from('profiles')
      .delete()
      .eq('id', profileId);

    if (!error && user) {
      await loadProfiles(user.id);
    }
  };

  const setAsPrimary = async (profileId: string) => {
    if (!user) return;

    // First, unset all primary flags
    await supabase
      .from('profiles')
      .update({ is_primary: false })
      .eq('user_id', user.id);

    // Then set the new primary
    const { error } = await supabase
      .from('profiles')
      .update({ is_primary: true })
      .eq('id', profileId);

    if (!error) {
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
              href="/calculator"
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

        {/* My Profile Section */}
        <div className="card mb-4">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Мой профиль
          </h2>

          {!primaryProfile ? (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-4">
                У вас ещё нет основного профиля
              </p>
              <Link
                href="/join"
                className="inline-block px-6 py-2 bg-brand-green text-white rounded-lg hover:bg-brand-green-hover transition-colors"
              >
                Создать профиль
              </Link>
            </div>
          ) : (
            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-gray-900 text-lg">
                    {primaryProfile.name}
                  </span>
                  {primaryProfile.username && (
                    <span className="text-sm text-gray-500">
                      @{primaryProfile.username}
                    </span>
                  )}
                </div>
                <div className="text-sm text-gray-500 mt-1">
                  {formatDate(primaryProfile.birth_date)} | {primaryProfile.birth_city || 'Город не указан'} | {primaryProfile.ayanamsa}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Link
                  href={`/calculator?profile=${primaryProfile.id}`}
                  className="text-sm px-3 py-1.5 bg-white text-brand-green border border-brand-green rounded-lg hover:bg-brand-green hover:text-white transition-colors"
                >
                  Гороскоп
                </Link>
                <Link
                  href="/dashboard/settings"
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Настройки
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Friend Profiles Section */}
        <div className="card">
          <div
            className="flex items-center justify-between cursor-pointer"
            onClick={() => setShowFriends(!showFriends)}
          >
            <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
              Сохранённые расчёты
              <span className="text-sm font-normal text-gray-500">
                ({friendProfiles.length})
              </span>
            </h2>
            <button className="text-gray-400 hover:text-gray-600">
              {showFriends ? '▼' : '▶'}
            </button>
          </div>

          {showFriends && (
            <>
              {friendProfiles.length === 0 ? (
                <div className="text-center py-6 mt-4">
                  <p className="text-gray-400 text-sm">
                    Здесь будут гороскопы друзей и знакомых
                  </p>
                  <Link
                    href="/calculator"
                    className="text-brand-green hover:text-brand-green-hover text-sm mt-2 inline-block"
                  >
                    + Добавить расчёт
                  </Link>
                </div>
              ) : (
                <div className="space-y-3 mt-4">
                  {friendProfiles.map((profile) => (
                    <div
                      key={profile.id}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                    >
                      <div>
                        <span className="font-medium text-gray-900">
                          {profile.name}
                        </span>
                        <div className="text-sm text-gray-500 mt-1">
                          {formatDate(profile.birth_date)} | {profile.birth_city || 'Город не указан'} | {profile.ayanamsa}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {!primaryProfile && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setAsPrimary(profile.id);
                            }}
                            className="text-sm text-blue-500 hover:text-blue-700"
                            title="Сделать основным профилем"
                          >
                            Мой профиль
                          </button>
                        )}
                        <Link
                          href={`/calculator?profile=${profile.id}`}
                          className="text-sm text-brand-green hover:text-brand-green-hover"
                        >
                          Открыть
                        </Link>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteProfile(profile.id, false);
                          }}
                          className="text-sm text-gray-400 hover:text-red-500"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
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
            Найти людей
          </Link>
          {primaryProfile?.username && (
            <Link
              href={`/profile/${primaryProfile.username}`}
              className="flex-1 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition-colors text-center"
            >
              Публичный профиль
            </Link>
          )}
        </div>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="card text-center">
            <div className="text-2xl font-semibold text-gray-900">
              {friendProfiles.length}
            </div>
            <div className="text-sm text-gray-500">Расчётов</div>
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
