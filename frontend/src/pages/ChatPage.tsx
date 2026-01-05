import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ChatMessage as ChatMessageType } from '@/types/prompt';
import { Message as ConversationMessage } from '@/types/conversation';
import { promptService } from '@/services/promptService';
import { conversationService } from '@/services/conversationService';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ModelSelector from '@/components/ModelSelector';
import ConversationList from '@/components/ConversationList';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Trash2, Loader2, MessageSquare, X } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { DEFAULT_MODEL } from '@/constants/models';

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [showSidebar, setShowSidebar] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    // localStorage에서 저장된 모델 불러오기
    const saved = localStorage.getItem('selectedModel');
    return saved || DEFAULT_MODEL;
  });
  const [maxTokens, setMaxTokens] = useState<number>(() => {
    // localStorage에서 저장된 max_tokens 불러오기
    const saved = localStorage.getItem('maxTokens');
    return saved ? parseInt(saved, 10) : 1000;
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  // 모델 변경 시 localStorage에 저장
  useEffect(() => {
    localStorage.setItem('selectedModel', selectedModel);
  }, [selectedModel]);

  // max_tokens 변경 시 localStorage에 저장
  useEffect(() => {
    localStorage.setItem('maxTokens', maxTokens.toString());
  }, [maxTokens]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  // 대화 세션 조회
  const { data: conversation } = useQuery({
    queryKey: ['conversation', currentConversationId],
    queryFn: () => conversationService.getConversation(currentConversationId!),
    enabled: !!currentConversationId,
  });

  // 대화 세션 로드 시 메시지 불러오기
  useEffect(() => {
    if (conversation && conversation.messages) {
      const loadedMessages: ChatMessageType[] = conversation.messages.map((msg: ConversationMessage) => ({
        role: msg.role as 'user' | 'assistant' | 'system',
        content: msg.content,
        timestamp: new Date(msg.created_at),
      }));
      setMessages(loadedMessages);
      
      // 모델과 설정도 복원
      if (conversation.model) {
        setSelectedModel(conversation.model);
      }
      if (conversation.max_tokens) {
        setMaxTokens(conversation.max_tokens);
      }
    }
  }, [conversation]);

  // 대화 세션 선택 핸들러
  const handleSelectConversation = (conversationId: number) => {
    if (conversationId === 0) {
      // 새 대화 시작
      setCurrentConversationId(null);
      setMessages([]);
      setStreamingMessage('');
    } else {
      setCurrentConversationId(conversationId);
    }
  };

  const mutation = useMutation({
    mutationFn: async (userMessage: string) => {
      const newUserMessage: ChatMessageType = {
        role: 'user',
        content: userMessage,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, newUserMessage]);

      const chatMessages: ChatMessageType[] = [...messages, newUserMessage];
      
      setIsStreaming(true);
      setStreamingMessage('');

      let fullResponse = '';

      await promptService.streamChatCompletion(
        {
          messages: chatMessages,
          model: selectedModel,
          temperature: 0.7,
          max_tokens: maxTokens,
          stream: true,
          conversation_id: currentConversationId || undefined,
        },
        (chunk) => {
          fullResponse += chunk;
          setStreamingMessage(fullResponse);
        },
        (conversationId) => {
          const assistantMessage: ChatMessageType = {
            role: 'assistant',
            content: fullResponse,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setStreamingMessage('');
          setIsStreaming(false);
          
          // 새로 생성된 대화 세션 ID 설정
          if (conversationId && !currentConversationId) {
            setCurrentConversationId(conversationId);
          }
          
          // 대화 목록 새로고침
          queryClient.invalidateQueries({ queryKey: ['conversations'] });
        },
        (error) => {
          console.error('Streaming error:', error);
          const errorMessage: ChatMessageType = {
            role: 'assistant',
            content: `오류가 발생했습니다: ${error.message}`,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, errorMessage]);
          setStreamingMessage('');
          setIsStreaming(false);
        }
      );
    },
  });

  const handleSend = (message: string) => {
    mutation.mutate(message);
  };

  const handleClear = () => {
    setMessages([]);
    setStreamingMessage('');
    setCurrentConversationId(null);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      {showSidebar && (
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="font-semibold text-gray-900">대화 목록</h2>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSidebar(false)}
              className="h-8 w-8 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <Button
              variant="outline"
              className="w-full mb-4"
              onClick={() => handleSelectConversation(0)}
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              새 대화 시작
            </Button>
            <ConversationList
              onSelectConversation={handleSelectConversation}
              selectedConversationId={currentConversationId}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">AI 채팅</h1>
              <p className="text-sm text-gray-500">
                {user?.full_name || user?.email}님, 안녕하세요!
              </p>
            </div>
            <div className="flex gap-2">
              {!showSidebar && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowSidebar(true)}
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  대화 목록
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/')}
              >
                홈으로
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClear}
                disabled={messages.length === 0 && !isStreaming}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                대화 초기화
              </Button>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ModelSelector
              value={selectedModel}
              onChange={setSelectedModel}
              disabled={isStreaming}
            />
            <div className="flex items-center gap-2">
              <Label htmlFor="max-tokens" className="text-xs text-gray-500 font-medium whitespace-nowrap">
                최대 토큰
              </Label>
              <Input
                id="max-tokens"
                type="number"
                min="1"
                value={maxTokens}
                onChange={(e) => {
                  const value = parseInt(e.target.value, 10);
                  if (!isNaN(value) && value >= 1) {
                    setMaxTokens(value);
                  }
                }}
                disabled={isStreaming}
                className="w-24 text-sm"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.length === 0 && !isStreaming && (
            <div className="text-center text-gray-500 mt-20">
              <p className="text-lg mb-2">안녕하세요! 무엇을 도와드릴까요?</p>
              <p className="text-sm">메시지를 입력하여 대화를 시작하세요.</p>
            </div>
          )}

          {messages.map((message, index) => (
            <ChatMessage key={index} message={message} />
          ))}

          {isStreaming && streamingMessage && (
            <div className="flex gap-4 p-4 rounded-lg bg-gray-50 justify-start">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <Loader2 className="w-5 h-5 text-gray-600 animate-spin" />
                </div>
              </div>
              <div className="flex-1 max-w-3xl">
                <div className="rounded-lg px-4 py-2 bg-white border border-gray-200">
                  <p className="whitespace-pre-wrap break-words">{streamingMessage}</p>
                  <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        isLoading={isStreaming}
        disabled={mutation.isPending}
      />
      </div>
    </div>
  );
}
