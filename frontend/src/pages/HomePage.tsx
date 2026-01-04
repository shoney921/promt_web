import { useAuthStore } from '@/store/authStore';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LogOut, MessageSquare, Sparkles } from 'lucide-react';

export default function HomePage() {
  const { user, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate('/login');
  };

  const handleStartChat = () => {
    navigate('/chat');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">AI 프롬프트 웹</h1>
            <p className="text-muted-foreground mt-1">
              {user?.full_name || user?.email}님 환영합니다
            </p>
          </div>
          <Button onClick={handleLogout} variant="outline">
            <LogOut className="mr-2 h-4 w-4" />
            로그아웃
          </Button>
        </div>

        <Card className="max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              AI 대화 시작하기
            </CardTitle>
            <CardDescription>
              프롬프트를 입력하여 AI와 대화를 시작하세요
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-center text-muted-foreground py-4">
              OpenAI GPT 모델을 사용하여 실시간으로 AI와 대화할 수 있습니다.
            </p>
            <Button 
              onClick={handleStartChat} 
              className="w-full"
              size="lg"
            >
              <MessageSquare className="mr-2 h-5 w-5" />
              채팅 시작하기
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
