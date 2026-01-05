export interface Conversation {
  id: number;
  user_id: number;
  title: string | null;
  model: string | null;
  temperature: number | null;
  max_tokens: number | null;
  created_at: string;
  updated_at: string | null;
  messages?: Message[];
}

export interface ConversationListItem {
  id: number;
  user_id: number;
  title: string | null;
  model: string | null;
  created_at: string;
  updated_at: string | null;
  message_count: number;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  created_at: string;
}

export interface ConversationCreate {
  title?: string;
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

