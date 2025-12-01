'use client';

import { useState, useRef, useEffect } from 'react';

export interface ColumnConfig {
  id: string;
  label: string;
  enabled: boolean;
  fixed?: boolean;  // Cannot be disabled
}

interface TableColumnSelectorProps {
  columns: ColumnConfig[];
  onChange: (columns: ColumnConfig[]) => void;
}

export default function TableColumnSelector({ columns, onChange }: TableColumnSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleColumn = (columnId: string) => {
    const newColumns = columns.map(col =>
      col.id === columnId && !col.fixed
        ? { ...col, enabled: !col.enabled }
        : col
    );
    onChange(newColumns);
  };

  const enabledCount = columns.filter(c => c.enabled).length;

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900
                   px-2 py-1.5 rounded border border-gray-200 hover:border-gray-300
                   bg-white transition-colors"
      >
        <svg
          className="w-4 h-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
          />
        </svg>
        <span>Колонки ({enabledCount})</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1 w-56 bg-white border border-gray-200
                        rounded-lg shadow-lg z-50 py-2">
          <div className="px-3 py-1.5 border-b border-gray-100">
            <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Отображаемые колонки
            </span>
          </div>
          <div className="max-h-64 overflow-y-auto py-1">
            {columns.map((column) => (
              <label
                key={column.id}
                className={`flex items-center px-3 py-1.5 cursor-pointer hover:bg-gray-50
                           ${column.fixed ? 'opacity-60 cursor-not-allowed' : ''}`}
              >
                <input
                  type="checkbox"
                  checked={column.enabled}
                  onChange={() => toggleColumn(column.id)}
                  disabled={column.fixed}
                  className="w-4 h-4 text-gray-900 border-gray-300 rounded
                           focus:ring-gray-500 focus:ring-offset-0"
                />
                <span className="ml-2.5 text-sm text-gray-700">
                  {column.label}
                  {column.fixed && <span className="text-gray-400 ml-1">(обяз.)</span>}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Default planet columns configuration
export const DEFAULT_PLANET_COLUMNS: ColumnConfig[] = [
  { id: 'name', label: 'Планета', enabled: true, fixed: true },
  { id: 'sign', label: 'Знак', enabled: true },
  { id: 'degrees', label: 'Градусы', enabled: true },
  { id: 'retrograde', label: 'Ретроград', enabled: true },
  { id: 'nakshatra', label: 'Накшатра', enabled: true },
  { id: 'house', label: 'Дом', enabled: true },
  { id: 'sign_lord', label: 'Управитель знака', enabled: true },
  { id: 'nakshatra_lord', label: 'Управитель накшатры', enabled: false },
  { id: 'houses_owned', label: 'Управляет домами', enabled: false },
  { id: 'dignity', label: 'Достоинство', enabled: false },
  { id: 'conjunctions', label: 'Соединения', enabled: false },
  { id: 'aspects_giving', label: 'Аспектирует дома', enabled: false },
  { id: 'aspects_receiving', label: 'Аспекты от планет', enabled: false },
];

// Default house columns configuration
export const DEFAULT_HOUSE_COLUMNS: ColumnConfig[] = [
  { id: 'house', label: 'Дом', enabled: true, fixed: true },
  { id: 'sign', label: 'Знак', enabled: true },
  { id: 'occupants', label: 'Планеты', enabled: true },
  { id: 'lord', label: 'Управитель', enabled: false },
  { id: 'aspects_received', label: 'Аспекты', enabled: false },
];
