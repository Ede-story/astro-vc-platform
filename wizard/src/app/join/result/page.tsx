'use client';

export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DopamineHit from '@/components/wizard/DopamineHit';
import { DigitalTwin } from '@/types/astro';

export default function ResultPage() {
  const router = useRouter();
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get digital twin from sessionStorage
    const stored = sessionStorage.getItem('digitalTwin');
    if (stored) {
      try {
        setDigitalTwin(JSON.parse(stored));
      } catch {
        router.push('/join');
      }
    } else {
      router.push('/join');
    }
    setLoading(false);
  }, [router]);

  const handleContinue = () => {
    router.push('/join/profile');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-gray-500">Загрузка...</div>
      </div>
    );
  }

  if (!digitalTwin) {
    return null;
  }

  return <DopamineHit digitalTwin={digitalTwin} onContinue={handleContinue} />;
}
