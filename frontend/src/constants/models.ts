export interface ModelOption {
  value: string;
  label: string;
  description: string;
  category: "gpt-4" | "gpt-3.5";
}

export const AVAILABLE_MODELS: ModelOption[] = [
  {
    value: "gpt-4o-mini",
    label: "GPT-4o Mini",
    description: "빠르고 저렴한 모델",
    category: "gpt-4",
  },
  {
    value: "gpt-4o",
    label: "GPT-4o",
    description: "최신 고성능 모델",
    category: "gpt-4",
  },
  {
    value: "gpt-4-turbo",
    label: "GPT-4 Turbo",
    description: "고성능 모델",
    category: "gpt-4",
  },
  {
    value: "gpt-4",
    label: "GPT-4",
    description: "표준 고성능 모델",
    category: "gpt-4",
  },
  {
    value: "gpt-3.5-turbo",
    label: "GPT-3.5 Turbo",
    description: "빠른 응답 모델",
    category: "gpt-3.5",
  },
];

export const DEFAULT_MODEL = "gpt-4o-mini";
