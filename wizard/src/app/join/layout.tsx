'use client';

import { WizardProvider } from '@/contexts/WizardContext';
import Link from 'next/link';

export default function WizardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <WizardProvider>
      <div className="min-h-screen bg-white">
        {/* Header */}
        <header className="fixed top-0 left-0 right-0 bg-white/80 backdrop-blur-sm border-b border-gray-100 z-50">
          <div className="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link href="/" className="text-xl font-semibold text-gray-900">
              StarMeet
            </Link>
            <Link
              href="/login"
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              Уже есть аккаунт?
            </Link>
          </div>
        </header>

        {/* Main content */}
        <main className="pt-20 pb-8 px-4">
          <div className="max-w-2xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </WizardProvider>
  );
}
