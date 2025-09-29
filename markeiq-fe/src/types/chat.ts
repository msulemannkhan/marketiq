import { Product } from './product';

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  products_mentioned?: Product[];
  citations?: Citation[];
  recommendations?: Recommendation[];
  suggested_actions?: string[];
  isTyping?: boolean;
}

export interface Citation {
  product_name: string;
  sku: string;
  url: string;
  relevance_score: number;
}

export interface ChatRequest {
  message: string;
  session_id: string;
  context?: Record<string, unknown>;
}

export interface Recommendation {
  variant_id: string;
  product_name: string;
  configuration: {
    brand: string;
    processor: string;
    memory: string;
    storage: string;
    display: string;
    price: number;
  };
  price: number;
  score: number;
  rationale: string;
}

export interface ChatResponse {
  response: string;
  citations: Citation[];
  recommendations: Recommendation[];
  session_id: string;
  timestamp: string;
  next_suggestions: string[];
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  created_at: Date;
  updated_at: Date;
}

export interface UseChatOptions {
  onMessage?: (message: ChatMessage) => void;
  onError?: (error: string) => void;
  onProductsUpdate?: (products: Product[]) => void;
}

export interface UseChatReturn {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  retryLastMessage: () => Promise<void>;
  suggestedActions: string[];
  products: Product[];
  citations: Citation[];
}
