'use client';

interface InterestOption {
  id: string;
  label: string;
  icon: string;
}

interface InterestSelectorProps {
  title: string;
  options: InterestOption[];
  selected: string[];
  onChange: (selected: string[]) => void;
  maxSelect?: number;
}

export default function InterestSelector({
  title,
  options,
  selected,
  onChange,
  maxSelect,
}: InterestSelectorProps) {
  const handleToggle = (id: string) => {
    if (selected.includes(id)) {
      onChange(selected.filter(s => s !== id));
    } else {
      if (maxSelect && selected.length >= maxSelect) {
        // Replace last selected
        onChange([...selected.slice(0, -1), id]);
      } else {
        onChange([...selected, id]);
      }
    }
  };

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 mb-3">{title}</h3>
      <div className="grid grid-cols-2 gap-3">
        {options.map((option) => (
          <button
            key={option.id}
            type="button"
            onClick={() => handleToggle(option.id)}
            className={`p-4 rounded-xl border-2 text-left transition-all ${
              selected.includes(option.id)
                ? 'border-gray-700 bg-gray-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <span className="text-2xl mb-2 block">{option.icon}</span>
            <span className="text-sm font-medium text-gray-900">{option.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
