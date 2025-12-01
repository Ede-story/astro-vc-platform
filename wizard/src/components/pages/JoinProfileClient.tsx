'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import WizardProgress from '@/components/wizard/WizardProgress';
import { createClient } from '@/lib/supabase/client';

export default function JoinProfileClient() {
  const router = useRouter();
  const supabase = createClient();

  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [bio, setBio] = useState('');
  const [career, setCareer] = useState('');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  const [usernameStatus, setUsernameStatus] = useState<'idle' | 'checking' | 'available' | 'taken'>('idle');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Check if we have birth data
  useEffect(() => {
    const birthData = sessionStorage.getItem('birthData');
    const digitalTwin = sessionStorage.getItem('digitalTwin');
    if (!birthData || !digitalTwin) {
      router.push('/join');
    }
  }, [router]);

  // Username validation with debounce
  useEffect(() => {
    if (!username || username.length < 3) {
      setUsernameStatus('idle');
      return;
    }

    // Username format validation
    if (!/^[a-z0-9_]+$/.test(username)) {
      setUsernameStatus('idle');
      return;
    }

    setUsernameStatus('checking');

    const timeoutId = setTimeout(async () => {
      // Check if username is taken
      const { data, error } = await supabase
        .from('profiles')
        .select('username')
        .eq('username', username)
        .single();

      if (error && error.code === 'PGRST116') {
        // No rows returned = username available
        setUsernameStatus('available');
      } else if (data) {
        setUsernameStatus('taken');
      } else {
        setUsernameStatus('available');
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [username, supabase]);

  // Handle avatar selection
  const handleAvatarChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Выберите изображение');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Максимальный размер файла — 5MB');
      return;
    }

    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!fullName.trim()) {
      setError('Введите ваше имя');
      return;
    }

    if (!username || username.length < 3) {
      setError('Username должен быть не менее 3 символов');
      return;
    }

    if (!/^[a-z0-9_]+$/.test(username)) {
      setError('Username может содержать только латинские буквы, цифры и _');
      return;
    }

    if (usernameStatus === 'taken') {
      setError('Этот username уже занят');
      return;
    }

    setLoading(true);

    try {
      // Store profile data in sessionStorage
      let avatarUrl = null;

      // If avatar was selected, we'll upload it later when saving to DB
      if (avatarFile) {
        // Convert to base64 for temporary storage
        const reader = new FileReader();
        avatarUrl = await new Promise<string>((resolve) => {
          reader.onload = () => resolve(reader.result as string);
          reader.readAsDataURL(avatarFile);
        });
      }

      sessionStorage.setItem('profileData', JSON.stringify({
        fullName,
        username,
        bio,
        career,
        avatarUrl,
        avatarFile: avatarFile ? avatarFile.name : null,
      }));

      // Navigate to calibration (personality test)
      router.push('/join/calibration');
    } catch (err) {
      setError('Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8">
      <WizardProgress currentStep={2} totalSteps={4} />

      <div className="text-center mb-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-2">
          Расскажите о себе
        </h1>
        <p className="text-gray-500">
          Эта информация будет видна другим пользователям
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Avatar */}
        <div className="flex flex-col items-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleAvatarChange}
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="group relative w-24 h-24 rounded-full overflow-hidden bg-gray-100 border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
          >
            {avatarPreview ? (
              <>
                <img
                  src={avatarPreview}
                  alt="Avatar"
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
              </>
            ) : (
              <div className="flex items-center justify-center h-full">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
            )}
          </button>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="mt-2 text-sm text-gray-500 hover:text-gray-700"
          >
            {avatarPreview ? 'Изменить фото' : 'Добавить фото'}
          </button>
        </div>

        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Имя
          </label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Как вас зовут?"
            className="input-field text-lg"
            maxLength={50}
          />
        </div>

        {/* Username */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Username
          </label>
          <div className="relative flex items-center">
            <span className="absolute left-3 text-gray-400 pointer-events-none select-none z-10">@</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
              placeholder="username"
              className="input-field text-lg"
              style={{ paddingLeft: '28px' }}
              maxLength={30}
            />
            {usernameStatus !== 'idle' && (
              <span className="absolute right-4 top-1/2 -translate-y-1/2">
                {usernameStatus === 'checking' && (
                  <svg className="w-5 h-5 text-gray-400 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                )}
                {usernameStatus === 'available' && (
                  <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
                {usernameStatus === 'taken' && (
                  <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                )}
              </span>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Только латинские буквы, цифры и _
          </p>
        </div>

        {/* Bio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            О себе
            <span className="text-gray-400 font-normal"> (опционально)</span>
          </label>
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            placeholder="Расскажите немного о себе..."
            className="input-field text-lg resize-none overflow-y-auto"
            rows={4}
          />
        </div>

        {/* Career */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Карьера
            <span className="text-gray-400 font-normal"> (опционально)</span>
          </label>
          <textarea
            value={career}
            onChange={(e) => setCareer(e.target.value)}
            placeholder="Кем работаете? Чем занимаетесь?"
            className="input-field text-lg resize-none overflow-y-auto"
            rows={3}
          />
          <p className="text-xs text-gray-500 mt-1">
            Поможет найти профессиональные связи
          </p>
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
          disabled={loading || usernameStatus === 'taken' || usernameStatus === 'checking'}
          className="w-full bg-brand-graphite text-white font-medium py-4 px-6 rounded-xl hover:bg-brand-graphite-hover transition-colors duration-150 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Загрузка...' : 'Продолжить'}
        </button>

        {/* Skip */}
        <button
          type="button"
          onClick={() => router.push('/join/calibration')}
          className="w-full text-gray-500 hover:text-gray-700 text-sm py-2"
        >
          Заполнить позже
        </button>
      </form>
    </div>
  );
}
