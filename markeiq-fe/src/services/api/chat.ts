import { ChatRequest, ChatResponse, ChatMessage } from '@/types/chat';
import { makeRequest } from '@/services/utils';


export class ChatService {

  static async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    return makeRequest<ChatResponse>('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }


  static generateSessionId(): string {
    return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static saveSessionToStorage(sessionId: string, messages: ChatMessage[]): void {
    if (typeof window !== 'undefined') {
      try {
        const sessionData = {
          sessionId,
          messages,
          timestamp: new Date().toISOString()
        };
        localStorage.setItem(`chat_session_${sessionId}`, JSON.stringify(sessionData));
      } catch (error) {
        console.warn('Failed to save chat session to storage:', error);
      }
    }
  }

  static loadSessionFromStorage(sessionId: string): ChatMessage[] | null {
    if (typeof window !== 'undefined') {
      try {
        const sessionData = localStorage.getItem(`chat_session_${sessionId}`);
        return sessionData ? JSON.parse(sessionData).messages : null;
      } catch (error) {
        console.warn('Failed to load chat session from storage:', error);
        return null;
      }
    }
    return null;
  }

  static clearSessionFromStorage(sessionId: string): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(`chat_session_${sessionId}`);
    }
  }

  static getAllSessions(): string[] {
    if (typeof window !== 'undefined') {
      const sessions: string[] = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key?.startsWith('chat_session_')) {
          sessions.push(key.replace('chat_session_', ''));
        }
      }
      return sessions;
    }
    return [];
  }
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}
