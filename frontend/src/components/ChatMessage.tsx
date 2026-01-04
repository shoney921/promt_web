import { ChatMessage as ChatMessageType } from '@/types/prompt';
import { User, Bot } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex gap-4 p-4 rounded-lg',
        isUser ? 'bg-blue-50 justify-end' : 'bg-gray-50 justify-start'
      )}
    >
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
            <Bot className="w-5 h-5 text-gray-600" />
          </div>
        </div>
      )}
      
      <div
        className={cn(
          'flex-1 max-w-3xl',
          isUser && 'flex flex-col items-end'
        )}
      >
        <div
          className={cn(
            'rounded-lg px-4 py-2',
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-white border border-gray-200 text-gray-900'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        {message.timestamp && (
          <span className="text-xs text-gray-500 mt-1">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
            <User className="w-5 h-5 text-white" />
          </div>
        </div>
      )}
    </div>
  );
}
