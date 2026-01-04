import { apiClient } from '@/lib/api';
import { Token, LoginCredentials, RegisterCredentials } from '@/types/auth';

export const authService = {
  async login(credentials: LoginCredentials): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/login', credentials);
    return response.data;
  },

  async register(credentials: RegisterCredentials): Promise<Token> {
    const response = await apiClient.post<Token>('/auth/register', credentials);
    return response.data;
  },
};
