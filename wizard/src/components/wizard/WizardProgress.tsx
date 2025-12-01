'use client';

interface WizardProgressProps {
  currentStep: number;
  totalSteps: number;
}

const STEP_LABELS = [
  'Данные рождения',
  'Ваш профиль',
  'Калибровка',
  'Интересы',
];

export default function WizardProgress({ currentStep, totalSteps }: WizardProgressProps) {
  // Don't show progress on result screen (step 0 means result)
  if (currentStep === 0) return null;

  return (
    <div className="w-full max-w-md mx-auto mb-8">
      {/* Step indicator */}
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-500">
          Шаг {currentStep} из {totalSteps}
        </span>
        <span className="text-sm text-gray-700 font-medium">
          {STEP_LABELS[currentStep - 1]}
        </span>
      </div>

      {/* Progress bar */}
      <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-brand-graphite transition-all duration-500 ease-out"
          style={{ width: `${(currentStep / totalSteps) * 100}%` }}
        />
      </div>

      {/* Step dots */}
      <div className="flex justify-between mt-3">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
          <div
            key={step}
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all duration-300 ${
              step < currentStep
                ? 'bg-brand-graphite text-white'
                : step === currentStep
                ? 'bg-brand-graphite text-white ring-2 ring-gray-300 ring-offset-2'
                : 'bg-gray-200 text-gray-500'
            }`}
          >
            {step < currentStep ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                  clipRule="evenodd"
                />
              </svg>
            ) : (
              step
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
