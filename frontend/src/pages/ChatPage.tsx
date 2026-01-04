import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { ChatMessage as ChatMessageType } from '@/types/prompt';
import { promptService } from '@/services/promptService';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import ModelSelector from '@/components/ModelSelector';
import { Button } from '@/components/ui/button';
import { Trash2, Loader2 } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { DEFAULT_MODEL } from '@/constants/models';

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    // localStorage에서 저장된 모델 불러오기
    const saved = localStorage.getItem('selectedModel');
    return saved || DEFAULT_MODEL;
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuthStore();

  // 모델 변경 시 localStorage에 저장
  useEffect(() => {
    localStorage.setItem('selectedModel', selectedModel);
  }, [selectedModel]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

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
          max_tokens: 1000,
          stream: true,
        },
        (chunk) => {
          fullResponse += chunk;
          setStreamingMessage(fullResponse);
        },
        () => {
          const assistantMessage: ChatMessageType = {
            role: 'assistant',
            content: fullResponse,
            timestamp: new Date(),
          };
          setMessages((prev) => [...prev, assistantMessage]);
          setStreamingMessage('');
          setIsStreaming(false);
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
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
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
          <div className="flex items-center">
            <ModelSelector
              value={selectedModel}
              onChange={setSelectedModel}
              disabled={isStreaming}
            />
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
  );
}
