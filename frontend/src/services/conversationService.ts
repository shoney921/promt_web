import { apiClient } from '@/lib/api';
import { Conversation, ConversationListItem, ConversationCreate, Message } from '@/types/conversation';

export const conversationService = {
  /**
   * 새 대화 세션 생성
   */
  async createConversation(data: ConversationCreate): Promise<Conversation> {
    const response = await apiClient.post<Conversation>('/conversations/', data);
    return response.data;
  },

  /**
   * 대화 세션 목록 조회
   */
  async getConversations(skip = 0, limit = 50): Promise<ConversationListItem[]> {
    const response = await apiClient.get<ConversationListItem[]>('/conversations/', {
      params: { skip, limit },
    });
    return response.data;
  },

  /**
   * 특정 대화 세션 조회 (메시지 포함)
   */
  async getConversation(conversationId: number): Promise<Conversation> {
    const response = await apiClient.get<Conversation>(`/conversations/${conversationId}`);
    return response.data;
  },

  /**
   * 대화 세션 삭제
   */
  async deleteConversation(conversationId: number): Promise<void> {
    await apiClient.delete(`/conversations/${conversationId}`);
  },

  /**
   * 대화 세션 제목 업데이트
   */
  async updateConversationTitle(conversationId: number, title: string): Promise<Conversation> {
    const response = await apiClient.patch<Conversation>(
      `/conversations/${conversationId}/title?title=${encodeURIComponent(title)}`
    );
    return response.data;
  },
};

