import { apiClient } from './apiClient';
import { LoginRequest, LoginResponse, User } from '../types/auth';

class AuthService {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });

    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }

  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  }
}

export const authService = new AuthService();
