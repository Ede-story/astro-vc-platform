'use client';

import { useState } from 'react';

interface PersonalityReportProps {
  reportText: string;
  loading?: boolean;
  error?: string;
}

/**
 * PersonalityReport displays the LLM-generated personality analysis.
 * Supports collapsible sections and download functionality.
 */
export default function PersonalityReport({ reportText, loading, error }: PersonalityReportProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center gap-3 text-gray-500">
          <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-gray-600" />
          <span>Генерация отчёта о личности...</span>
        </div>
        <div className="mt-4 space-y-3">
          <div className="h-4 bg-gray-100 rounded w-full animate-pulse" />
          <div className="h-4 bg-gray-100 rounded w-5/6 animate-pulse" />
          <div className="h-4 bg-gray-100 rounded w-4/6 animate-pulse" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <div className="flex items-center gap-2 text-red-700">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span className="font-medium">Ошибка генерации отчёта</span>
        </div>
        <p className="mt-2 text-sm text-red-600">{error}</p>
      </div>
    );
  }

  if (!reportText) {
    return (
      <div className="card bg-gray-50">
        <div className="text-center py-8 text-gray-500">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>Отчёт о личности будет сгенерирован после расчёта</p>
        </div>
      </div>
    );
  }

  const handleDownload = () => {
    const blob = new Blob([reportText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `personality-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(reportText);
      alert('Отчёт скопирован в буфер обмена');
    } catch {
      alert('Не удалось скопировать отчёт');
    }
  };

  // Split text into paragraphs for better rendering
  const paragraphs = reportText.split('\n\n').filter(p => p.trim());

  return (
    <div className="card">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center gap-2 text-base font-medium text-gray-900 hover:text-gray-700"
          >
            <svg
              className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Отчёт о личности
          </button>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
            ~{Math.round(reportText.length / 1000)}k символов
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button
            onClick={handleCopy}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            title="Копировать"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </button>
          <button
            onClick={handleDownload}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
            title="Скачать"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="prose prose-sm max-w-none">
          {paragraphs.map((paragraph, idx) => {
            // Check if paragraph is a header (starts with # or **)
            if (paragraph.startsWith('**') && paragraph.endsWith('**')) {
              return (
                <h3 key={idx} className="text-lg font-semibold text-gray-900 mt-6 mb-3">
                  {paragraph.replace(/\*\*/g, '')}
                </h3>
              );
            }

            // Check for section headers (lines ending with :)
            if (paragraph.endsWith(':') && paragraph.length < 100) {
              return (
                <h4 key={idx} className="text-base font-medium text-gray-800 mt-4 mb-2">
                  {paragraph}
                </h4>
              );
            }

            // Check for bullet points
            if (paragraph.includes('\n- ') || paragraph.startsWith('- ')) {
              const lines = paragraph.split('\n');
              return (
                <ul key={idx} className="list-disc list-inside space-y-1 text-gray-700 my-3">
                  {lines.map((line, lineIdx) => {
                    const text = line.startsWith('- ') ? line.substring(2) : line;
                    return text.trim() ? (
                      <li key={lineIdx}>{text}</li>
                    ) : null;
                  })}
                </ul>
              );
            }

            // Regular paragraph
            return (
              <p key={idx} className="text-gray-700 leading-relaxed my-3">
                {paragraph}
              </p>
            );
          })}
        </div>
      )}

      {/* Collapsed indicator */}
      {!isExpanded && (
        <div className="text-gray-400 text-sm italic">
          Нажмите для раскрытия полного отчёта...
        </div>
      )}
    </div>
  );
}
