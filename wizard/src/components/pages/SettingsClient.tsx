'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';
import { User } from '@supabase/supabase-js';
import { personalitySliders } from '@/data/personality-sliders';

interface Profile {
  id: string;
  name: string;
  username: string | null;
  bio: string | null;
  career: string | null;
  is_public: boolean;
  is_primary: boolean;
  birth_date: string;
  birth_time: string | null;
  birth_city: string | null;
  ayanamsa: string;
  seeking: string[];
  offerings: string[];
  psych_scores: Record<string, number>;
  psych_completed_at: string | null;
}

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

export default function SettingsClient() {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Form state
  const [name, setName] = useState('');
  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');
  const [career, setCareer] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [seeking, setSeeking] = useState<string[]>([]);
  const [offerings, setOfferings] = useState<string[]>([]);
  const [psychScores, setPsychScores] = useState<Record<string, number>>({});

  // Calibration edit mode
  const [editingCalibration, setEditingCalibration] = useState(false);
  const [tempPsychScores, setTempPsychScores] = useState<Record<string, number>>({});

  const router = useRouter();
  const supabase = createClient();

  useEffect(() => {
    const loadData = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
        return;
      }
      setUser(user);

      // Load primary profile
      const { data: profileData, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('user_id', user.id)
        .eq('is_primary', true)
        .single();

      if (error || !profileData) {
        // Try to get any profile
        const { data: anyProfile } = await supabase
          .from('profiles')
          .select('*')
          .eq('user_id', user.id)
          .limit(1)
          .single();

        if (anyProfile) {
          setProfile(anyProfile);
          populateForm(anyProfile);
        }
      } else {
        setProfile(profileData);
        populateForm(profileData);
      }

      setLoading(false);
    };

    loadData();
  }, [router, supabase]);

  const populateForm = (p: Profile) => {
    setName(p.name || '');
    setUsername(p.username || '');
    setBio(p.bio || '');
    setCareer(p.career || '');
    setIsPublic(p.is_public || false);
    setSeeking(p.seeking || []);
    setOfferings(p.offerings || []);
    setPsychScores(p.psych_scores || {});
    setTempPsychScores(p.psych_scores || {});
  };

  const handleSave = async () => {
    if (!profile) return;

    setSaving(true);
    setMessage(null);

    try {
      const updateData: Record<string, unknown> = {
        name: name.trim(),
        username: username.trim() || null,
        bio: bio.trim() || null,
        career: career.trim() || null,
        is_public: isPublic,
        seeking: seeking,
        offerings: offerings,
      };

      // Include psych scores if they were edited
      if (editingCalibration) {
        updateData.psych_scores = tempPsychScores;
        updateData.psych_completed_at = new Date().toISOString();
      }

      const { error } = await supabase
        .from('profiles')
        .update(updateData)
        .eq('id', profile.id);

      if (error) {
        if (error.code === '23505') {
          setMessage({ type: 'error', text: 'Этот username уже занят' });
        } else {
          setMessage({ type: 'error', text: error.message });
        }
      } else {
        setMessage({ type: 'success', text: 'Настройки сохранены' });
        // Update local profile state
        if (editingCalibration) {
          setPsychScores(tempPsychScores);
          setEditingCalibration(false);
        }
        setProfile({
          ...profile,
          name,
          username,
          bio,
          career,
          is_public: isPublic,
          seeking,
          offerings,
          psych_scores: editingCalibration ? tempPsychScores : psychScores,
        });
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Ошибка сохранения' });
    } finally {
      setSaving(false);
    }
  };

  const toggleSeeking = (id: string) => {
    setSeeking(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const toggleOffering = (id: string) => {
    setOfferings(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const getLabel = (value: number, labels: [string, string, string]) => {
    if (value <= 33) return labels[0];
    if (value <= 66) return labels[1];
    return labels[2];
  };

  const hasPsychResults = Object.keys(psychScores).length > 0 &&
    Object.values(psychScores).some(v => v !== 50);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">Профиль не найден</p>
          <Link href="/join" className="text-brand-green hover:text-brand-green-hover">
            Создать профиль
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <header className="flex items-center justify-between mb-8">
          <Link href="/dashboard" className="text-gray-500 hover:text-gray-700">
            &larr; Назад
          </Link>
          <h1 className="text-xl font-semibold text-gray-900">Настройки</h1>
          <div className="w-16" />
        </header>

        {/* Message */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-lg ${
              message.type === 'success'
                ? 'bg-green-50 text-green-700 border border-green-200'
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}
          >
            {message.text}
          </div>
        )}

        {/* Birth Data Section (Read-only) */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Данные рождения</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Дата:</span>
              <p className="font-medium text-gray-900">{formatDate(profile.birth_date)}</p>
            </div>
            <div>
              <span className="text-gray-500">Время:</span>
              <p className="font-medium text-gray-900">{profile.birth_time || 'Не указано'}</p>
            </div>
            <div>
              <span className="text-gray-500">Город:</span>
              <p className="font-medium text-gray-900">{profile.birth_city || 'Не указан'}</p>
            </div>
            <div>
              <span className="text-gray-500">Ayanamsa:</span>
              <p className="font-medium text-gray-900">{profile.ayanamsa || 'Raman'}</p>
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-4">
            Для изменения данных рождения пересоздайте профиль
          </p>
        </div>

        {/* Privacy Section */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Приватность</h2>

          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">Публичный профиль</p>
              <p className="text-sm text-gray-500">
                Ваш профиль будет виден другим пользователям на странице Explore
              </p>
            </div>
            <button
              onClick={() => setIsPublic(!isPublic)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isPublic ? 'bg-brand-green' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isPublic ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>

        {/* Profile Info Section */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Информация о профиле</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Имя
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-green focus:border-transparent"
                placeholder="Ваше имя"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Username
              </label>
              <div className="flex items-center">
                <span className="text-gray-500 mr-1">@</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-green focus:border-transparent"
                  placeholder="username"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Только латинские буквы, цифры и _
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Карьера / Профессия
              </label>
              <input
                type="text"
                value={career}
                onChange={(e) => setCareer(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-green focus:border-transparent"
                placeholder="Чем вы занимаетесь?"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                О себе
              </label>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-green focus:border-transparent resize-none"
                placeholder="Расскажите о себе..."
              />
            </div>
          </div>
        </div>

        {/* Psychological Calibration Section */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Калибровка совместимости</h2>
            {!editingCalibration && (
              <button
                onClick={() => {
                  setEditingCalibration(true);
                  // Initialize with current values or defaults
                  const defaults = Object.fromEntries(
                    personalitySliders.map(s => [s.id, psychScores[s.id] ?? 50])
                  );
                  setTempPsychScores(defaults);
                }}
                className="text-sm text-brand-green hover:text-brand-green-hover"
              >
                {hasPsychResults ? 'Изменить' : 'Пройти тест'}
              </button>
            )}
          </div>

          {editingCalibration ? (
            <div className="space-y-6">
              {personalitySliders.map((slider) => (
                <div key={slider.id} className="bg-gray-50 rounded-xl p-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-3">
                    {slider.question}
                  </h4>

                  <div className="flex justify-between text-xs mb-2">
                    <span className="flex items-center gap-1">
                      <span>{slider.left.emoji}</span>
                      <span className="text-gray-600">{slider.left.label}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-gray-600">{slider.right.label}</span>
                      <span>{slider.right.emoji}</span>
                    </span>
                  </div>

                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={tempPsychScores[slider.id] ?? 50}
                    onChange={(e) => setTempPsychScores(prev => ({
                      ...prev,
                      [slider.id]: Number(e.target.value)
                    }))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, #2f3538 0%, #2f3538 ${tempPsychScores[slider.id] ?? 50}%, #e5e7eb ${tempPsychScores[slider.id] ?? 50}%, #e5e7eb 100%)`
                    }}
                  />

                  <div className="text-center mt-2">
                    <span className="text-xs text-gray-600 bg-white px-2 py-1 rounded-full">
                      {getLabel(tempPsychScores[slider.id] ?? 50, slider.labels)}
                    </span>
                  </div>
                </div>
              ))}

              <button
                onClick={() => {
                  setEditingCalibration(false);
                  setTempPsychScores(psychScores);
                }}
                className="w-full py-2 text-gray-500 text-sm hover:text-gray-700"
              >
                Отмена
              </button>
            </div>
          ) : hasPsychResults ? (
            <div className="space-y-3">
              {personalitySliders.map((slider) => {
                const value = psychScores[slider.id] ?? 50;
                return (
                  <div key={slider.id} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{slider.question}</span>
                    <span className="font-medium text-gray-900 bg-gray-100 px-2 py-1 rounded">
                      {getLabel(value, slider.labels)}
                    </span>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-500 text-sm mb-2">
                Тест не пройден
              </p>
              <p className="text-xs text-gray-400">
                Пройдите калибровку для более точного подбора совместимости
              </p>
            </div>
          )}
        </div>

        {/* Seeking Section */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Я ищу</h2>
          <div className="flex flex-wrap gap-2">
            {SEEKING_OPTIONS.map((option) => (
              <button
                key={option.id}
                onClick={() => toggleSeeking(option.id)}
                className={`px-4 py-2 rounded-full text-sm transition-colors ${
                  seeking.includes(option.id)
                    ? 'bg-blue-100 text-blue-700 border border-blue-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                }`}
              >
                {option.icon} {option.label}
              </button>
            ))}
          </div>
          {seeking.length === 0 && (
            <p className="text-xs text-gray-400 mt-2">
              Выберите, что вы ищете на платформе
            </p>
          )}
        </div>

        {/* Offerings Section */}
        <div className="card mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Я предлагаю</h2>
          <div className="flex flex-wrap gap-2">
            {OFFERING_OPTIONS.map((option) => (
              <button
                key={option.id}
                onClick={() => toggleOffering(option.id)}
                className={`px-4 py-2 rounded-full text-sm transition-colors ${
                  offerings.includes(option.id)
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                }`}
              >
                {option.icon} {option.label}
              </button>
            ))}
          </div>
          {offerings.length === 0 && (
            <p className="text-xs text-gray-400 mt-2">
              Выберите, чем можете быть полезны
            </p>
          )}
        </div>

        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={saving || !name.trim()}
          className="w-full py-3 bg-brand-graphite text-white font-medium rounded-xl hover:bg-brand-graphite-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saving ? 'Сохранение...' : 'Сохранить изменения'}
        </button>

        {/* Account Section */}
        <div className="card mt-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Аккаунт</h2>
          <p className="text-sm text-gray-500 mb-2">Email: {user?.email}</p>
          <button
            onClick={async () => {
              await supabase.auth.signOut();
              router.push('/login');
            }}
            className="text-red-500 hover:text-red-600 text-sm"
          >
            Выйти из аккаунта
          </button>
        </div>
      </div>
    </div>
  );
}
