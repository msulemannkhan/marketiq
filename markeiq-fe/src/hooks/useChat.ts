import { useState, useCallback, useRef, useEffect } from 'react';
import { ChatMessage, Citation, UseChatOptions, UseChatReturn } from '@/types/chat';
import { Product } from '@/types/product';
import { ChatService } from '@/services/api/chat';

export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { onMessage, onError, onProductsUpdate } = options;
  
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => ChatService.generateSessionId());
  const [suggestedActions, setSuggestedActions] = useState<string[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [citations, setCitations] = useState<Citation[]>([]);
  
  const lastMessageRef = useRef<ChatMessage | null>(null);

  // Load session from storage on mount
  useEffect(() => {
    const savedMessages = ChatService.loadSessionFromStorage(sessionId);
    if (savedMessages && savedMessages.length > 0) {
      setMessages(savedMessages);
    }
  }, [sessionId]);

  // Save messages to storage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      ChatService.saveSessionToStorage(sessionId, messages);
    }
  }, [messages, sessionId]);

  const addMessage = useCallback((message: ChatMessage) => {
    setMessages(prev => [...prev, message]);
    onMessage?.(message);
  }, [onMessage]);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      content: content.trim(),
      role: 'user',
      timestamp: new Date(),
    };

    addMessage(userMessage);
    setIsLoading(true);
    setError(null);

    // Add typing indicator
    const typingMessage: ChatMessage = {
      id: `typing_${Date.now()}`,
      content: '',
      role: 'assistant',
      timestamp: new Date(),
      isTyping: true,
    };

    addMessage(typingMessage);

    try {
      const response = await ChatService.sendMessage({
        message: content.trim(),
        session_id: sessionId,
      });

      // Remove typing indicator
      setMessages(prev => prev.filter(msg => !msg.isTyping));

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `assistant_${Date.now()}`,
        content: response.response,
        role: 'assistant',
        timestamp: new Date(),
        citations: response.citations,
        recommendations: response.recommendations,
        suggested_actions: response.next_suggestions,
      };

      addMessage(assistantMessage);

      // Update suggested actions
      setSuggestedActions(response.next_suggestions || []);

      // Update citations
      setCitations(response.citations || []);

      lastMessageRef.current = assistantMessage;
    } catch (err: unknown) {
      // Remove typing indicator
      setMessages(prev => prev.filter(msg => !msg.isTyping));
      
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      onError?.(errorMessage);  
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId, addMessage, onError]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setSuggestedActions([]);
    setProducts([]);
    setCitations([]);
    setError(null);
    ChatService.clearSessionFromStorage(sessionId);
  }, [sessionId]);

  const retryLastMessage = useCallback(async () => {
    if (!lastMessageRef.current || lastMessageRef.current.role !== 'user') return;
    
    // Remove the last assistant message if it exists
    setMessages(prev => {
      const lastUserIndex = prev.findLastIndex(msg => msg.role === 'user');
      if (lastUserIndex !== -1) {
        return prev.slice(0, lastUserIndex + 1);
      }
      return prev;
    });

    // Resend the last user message
    await sendMessage(lastMessageRef.current.content);
  }, [sendMessage]);

  return {
    messages,
    isLoading,
    error,
    sessionId,
    sendMessage,
    clearMessages,
    retryLastMessage,
    suggestedActions,
    products,
    citations,
  };
}
