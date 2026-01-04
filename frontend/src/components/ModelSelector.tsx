import { Select } from './ui/select';
import { AVAILABLE_MODELS, DEFAULT_MODEL, MODELS_BY_CATEGORY, CATEGORY_LABELS } from '@/constants/models';
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

  // 카테고리별로 그룹화된 옵션 생성
  const groupedOptions: { value: string; label: string; group?: string }[] = [];
  
  Object.entries(MODELS_BY_CATEGORY).forEach(([category, models]) => {
    if (models.length > 0) {
      // 해당 카테고리의 모델들 추가
      models.forEach((model) => {
        groupedOptions.push({
          value: model.value,
          label: `${model.label} - ${model.description}`,
          group: CATEGORY_LABELS[category],
        });
      });
    }
  });

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Settings className="w-4 h-4 text-gray-500 flex-shrink-0" />
      <div className="flex flex-col flex-1">
        <div className="flex items-center gap-2 mb-1">
          <label className="text-xs text-gray-500 font-medium">모델 선택</label>
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
          options={groupedOptions}
          className="w-full text-sm"
          disabled={disabled}
        />
        {showInfo && selectedModel && (
          <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded text-xs text-gray-700">
            <p className="font-medium">{selectedModel.label}</p>
            <p className="text-gray-600 mt-1">{selectedModel.description}</p>
            <p className="text-gray-500 mt-1">
              카테고리: {CATEGORY_LABELS[selectedModel.category] || selectedModel.category}
            </p>
            <p className="text-gray-500 mt-1">모델 ID: {selectedModel.value}</p>
          </div>
        )}
      </div>
    </div>
  );
}
