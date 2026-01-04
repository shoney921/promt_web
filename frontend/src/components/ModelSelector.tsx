import { Select } from './ui/select';
import { AVAILABLE_MODELS, DEFAULT_MODEL } from '@/constants/models';
import { Settings, Info } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface ModelSelectorProps {
  value: string;
  onChange: (model: string) => void;
  className?: string;
  disabled?: boolean;
}

export default function ModelSelector({ value, onChange, className, disabled = false }: ModelSelectorProps) {
  const selectedModel = AVAILABLE_MODELS.find((m) => m.value === value) || AVAILABLE_MODELS[0];
  const [showInfo, setShowInfo] = useState(false);

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Settings className="w-4 h-4 text-gray-500 flex-shrink-0" />
      <div className="flex flex-col flex-1">
        <div className="flex items-center gap-2 mb-1">
          <label className="text-xs text-gray-500">모델</label>
          <button
            type="button"
            onClick={() => setShowInfo(!showInfo)}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="모델 정보"
          >
            <Info className="w-3 h-3" />
          </button>
        </div>
        <Select
          value={value}
          onChange={(e) => onChange(e.target.value)}
          options={AVAILABLE_MODELS.map((model) => ({
            value: model.value,
            label: `${model.label} - ${model.description}`,
          }))}
          className="w-full text-sm"
          disabled={disabled}
        />
        {showInfo && selectedModel && (
          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-gray-700">
            <p className="font-medium">{selectedModel.label}</p>
            <p className="text-gray-600">{selectedModel.description}</p>
            <p className="text-gray-500 mt-1">카테고리: {selectedModel.category}</p>
          </div>
        )}
      </div>
    </div>
  );
}
