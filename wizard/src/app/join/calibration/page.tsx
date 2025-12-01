'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { personalitySliders } from '@/data/personality-sliders';

export default function CalibrationPage() {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [scores, setScores] = useState<Record<string, number>>(
    Object.fromEntries(personalitySliders.map(s => [s.id, 50]))
  );

  // Check if we have required data
  useEffect(() => {
    const birthData = sessionStorage.getItem('birthData');
    const digitalTwin = sessionStorage.getItem('digitalTwin');
    if (!birthData || !digitalTwin) {
      router.push('/join');
    }
  }, [router]);

  const current = personalitySliders[currentIndex];
  const progress = ((currentIndex + 1) / personalitySliders.length) * 100;

  const getLabel = (value: number, labels: [string, string, string]) => {
    if (value <= 33) return labels[0];
    if (value <= 66) return labels[1];
    return labels[2];
  };

  const handleSliderChange = (value: number) => {
    setScores(prev => ({ ...prev, [current.id]: value }));
  };

  const handleNext = () => {
    if (currentIndex < personalitySliders.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      // Save and navigate
      sessionStorage.setItem('psychScores', JSON.stringify(scores));
      router.push('/join/interests');
    }
  };

  const handleBack = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    } else {
      router.push('/join/profile');
    }
  };

  const handleSkip = () => {
    // Skip entire test, use defaults (50)
    sessionStorage.setItem('psychScores', JSON.stringify(scores));
    router.push('/join/interests');
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <div className="flex items-center justify-between max-w-md mx-auto">
          <button
            onClick={handleBack}
            className="p-2 -ml-2 text-gray-500 hover:text-gray-700 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 className="text-lg font-semibold text-gray-900">StarMeet</h1>
          <div className="w-9" /> {/* Spacer for centering */}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-8">
        {/* Title */}
        <div className="text-center mb-8">
          <div className="text-3xl mb-3">✨</div>
          <h2 className="text-xl font-semibold text-gray-900">
            Калибровка совместимости
          </h2>
          <p className="text-gray-500 text-sm mt-2">
            Вопрос {currentIndex + 1} из {personalitySliders.length}
          </p>
        </div>

        {/* Progress bar */}
        <div className="w-full max-w-md mb-8">
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-brand-graphite transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Question Card */}
        <div className="w-full max-w-md bg-gray-50 rounded-2xl p-6 mb-8">
          <h3 className="text-lg font-medium text-center text-gray-900 mb-8">
            {current.question}
          </h3>

          {/* Slider */}
          <div className="space-y-6">
            {/* Labels */}
            <div className="flex justify-between text-sm">
              <span className="flex items-center gap-2">
                <span className="text-xl">{current.left.emoji}</span>
                <span className="text-gray-600">{current.left.label}</span>
              </span>
              <span className="flex items-center gap-2">
                <span className="text-gray-600">{current.right.label}</span>
                <span className="text-xl">{current.right.emoji}</span>
              </span>
            </div>

            {/* Range input */}
            <input
              type="range"
              min="0"
              max="100"
              value={scores[current.id]}
              onChange={(e) => handleSliderChange(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb"
              style={{
                background: `linear-gradient(to right, #1f2937 0%, #1f2937 ${scores[current.id]}%, #e5e7eb ${scores[current.id]}%, #e5e7eb 100%)`
              }}
            />

            {/* Dynamic label */}
            <div className="text-center">
              <span className="inline-block px-4 py-2 bg-white rounded-full text-sm font-medium text-gray-700 shadow-sm border border-gray-100">
                {getLabel(scores[current.id], current.labels)}
              </span>
            </div>
          </div>
        </div>

        {/* Buttons */}
        <div className="w-full max-w-md space-y-3">
          <button
            onClick={handleNext}
            className="w-full py-4 bg-brand-graphite text-white rounded-xl font-medium hover:bg-brand-graphite-hover transition-colors text-lg"
          >
            {currentIndex < personalitySliders.length - 1 ? 'Далее' : 'Завершить'}
          </button>

          <button
            onClick={handleSkip}
            className="w-full py-3 text-gray-500 text-sm hover:text-gray-700 transition-colors"
          >
            Пропустить тест
          </button>
        </div>
      </div>

      {/* Slider thumb styles */}
      <style jsx>{`
        .slider-thumb::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #1f2937;
          cursor: pointer;
          border: 4px solid white;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
        .slider-thumb::-moz-range-thumb {
          width: 24px;
          height: 24px;
          border-radius: 50%;
          background: #1f2937;
          cursor: pointer;
          border: 4px solid white;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
        }
      `}</style>
    </div>
  );
}
