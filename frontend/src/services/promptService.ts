import { apiClient } from '@/lib/api';
import { PromptRequest, PromptResponse, ChatRequest, ChatMessage } from '@/types/prompt';
import { DEFAULT_MODEL } from '@/constants/models';

export const promptService = {
  /**
   * 단일 프롬프트 완성 요청
   */
  async getCompletion(request: PromptRequest): Promise<PromptResponse> {
    const response = await apiClient.post<PromptResponse>('/prompt/completion', {
      message: request.message,
      model: request.model || DEFAULT_MODEL,
      temperature: request.temperature ?? 0.7,
      max_tokens: request.max_tokens ?? 1000,
      stream: false,
    });
    return response.data;
  },

  /**
   * 채팅 완성 요청
   */
  async getChatCompletion(request: ChatRequest): Promise<PromptResponse> {
    const response = await apiClient.post<PromptResponse>('/prompt/chat', {
      messages: request.messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      })),
      model: request.model || DEFAULT_MODEL,
      temperature: request.temperature ?? 0.7,
      max_tokens: request.max_tokens ?? 1000,
      stream: false,
    });
    return response.data;
  },

  /**
   * 스트리밍 완성 요청
   */
  async streamCompletion(
    request: PromptRequest,
    onChunk: (chunk: string) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiClient.defaults.baseURL}/prompt/completion`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: request.message,
          model: request.model || DEFAULT_MODEL,
          temperature: request.temperature ?? 0.7,
          max_tokens: request.max_tokens ?? 1000,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete?.();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                onChunk(parsed.chunk);
              }
            } catch (e) {
              // JSON 파싱 실패 무시
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Unknown error'));
    }
  },

  /**
   * 스트리밍 채팅 완성 요청
   */
  async streamChatCompletion(
    request: ChatRequest,
    onChunk: (chunk: string) => void,
    onComplete?: () => void,
    onError?: (error: Error) => void
  ): Promise<void> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiClient.defaults.baseURL}/prompt/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          messages: request.messages.map(msg => ({
            role: msg.role,
            content: msg.content,
          })),
          model: request.model || DEFAULT_MODEL,
          temperature: request.temperature ?? 0.7,
          max_tokens: request.max_tokens ?? 1000,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete?.();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              onComplete?.();
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                onChunk(parsed.chunk);
              }
            } catch (e) {
              // JSON 파싱 실패 무시
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error('Unknown error'));
    }
  },
};
