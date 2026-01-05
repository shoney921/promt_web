import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { conversationService } from '@/services/conversationService';
import { ConversationListItem } from '@/types/conversation';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Trash2, MessageSquare, Clock } from 'lucide-react';

interface ConversationListProps {
  onSelectConversation: (conversationId: number) => void;
  selectedConversationId: number | null;
}

export default function ConversationList({
  onSelectConversation,
  selectedConversationId,
}: ConversationListProps) {
  const queryClient = useQueryClient();
  const [isDeleting, setIsDeleting] = useState<number | null>(null);

  const { data: conversations, isLoading } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => conversationService.getConversations(0, 50),
  });

  const deleteMutation = useMutation({
    mutationFn: (conversationId: number) => conversationService.deleteConversation(conversationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
      if (selectedConversationId === isDeleting) {
        onSelectConversation(0); // 새 대화로 전환
      }
      setIsDeleting(null);
    },
  });

  const handleDelete = async (e: React.MouseEvent, conversationId: number) => {
    e.stopPropagation();
    if (confirm('이 대화를 삭제하시겠습니까?')) {
      setIsDeleting(conversationId);
      deleteMutation.mutate(conversationId);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day} ${hours}:${minutes}`;
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 text-center text-gray-500">
        <div className="animate-pulse">로딩 중...</div>
      </div>
    );
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        <p>저장된 대화가 없습니다.</p>
        <p className="text-sm mt-2">새 대화를 시작해보세요!</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {conversations.map((conversation) => (
        <Card
          key={conversation.id}
          className={`p-3 cursor-pointer transition-colors ${
            selectedConversationId === conversation.id
              ? 'bg-blue-50 border-blue-300'
              : 'hover:bg-gray-50'
          }`}
          onClick={() => onSelectConversation(conversation.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <MessageSquare className="w-4 h-4 text-gray-500 flex-shrink-0" />
                <h3 className="font-medium text-sm truncate">
                  {conversation.title || '제목 없음'}
                </h3>
              </div>
              <div className="flex items-center gap-3 text-xs text-gray-500">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDate(conversation.updated_at || conversation.created_at)}
                </span>
                <span>{conversation.message_count}개 메시지</span>
                {conversation.model && (
                  <span className="text-gray-400">{conversation.model}</span>
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="ml-2 h-8 w-8 p-0 flex-shrink-0"
              onClick={(e) => handleDelete(e, conversation.id)}
              disabled={isDeleting === conversation.id}
            >
              <Trash2 className="w-4 h-4 text-red-500" />
            </Button>
          </div>
        </Card>
      ))}
    </div>
  );
}

