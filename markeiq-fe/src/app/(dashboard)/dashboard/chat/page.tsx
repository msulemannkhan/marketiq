"use client";

import { useState } from 'react';
import { useChat } from '@/hooks/useChat';
import { MessageList } from '@/components/chat/MessageList';
import { MessageInput } from '@/components/chat/MessageInput';
import { SuggestedActions } from '@/components/chat/SuggestedActions';
import { Button } from '@/components/ui/button';
import { RotateCcw, Trash2, AlertCircle } from 'lucide-react';

export default function ChatPage() {
  const [showWelcome, setShowWelcome] = useState(true);
  const {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
    retryLastMessage,
    suggestedActions,
  } = useChat({
    onMessage: () => {
      if (showWelcome) {
        setShowWelcome(false);
      }
    },
    onError: (error) => {
      console.error('Chat error:', error);
    },
  });

  const handleActionClick = (action: string) => {
    sendMessage(action);
  };

  const handleRetry = () => {
    retryLastMessage();
  };

  const handleClear = () => {
    clearMessages();
    setShowWelcome(true);
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-xl font-semibold text-foreground">
                AI Assistant
              </h1>
              <p className="text-sm text-muted-foreground">
                Get personalized laptop recommendations
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRetry}
                  disabled={isLoading}
                  className="gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Retry
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClear}
                  className="gap-2 text-destructive hover:text-destructive"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear
                </Button>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-destructive/10 border-b border-destructive/20 px-4 py-3">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">Error: {error}</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-0">
        {showWelcome && messages.length === 0 ? (
          /* Welcome State with Centered Input */
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            <div className="text-center max-w-2xl mx-auto space-y-8">
              <div className="space-y-4">
                <h2 className="text-4xl font-bold text-foreground">
                  Welcome to AI Assistant
                </h2>
                <p className="text-xl text-muted-foreground">
                  Get personalized laptop recommendations powered by AI. Ask questions about business laptops, compare models, and get expert advice.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-lg mx-auto">
                <div className="p-4 border rounded-xl bg-card hover:bg-accent/50 transition-colors">
                  <h3 className="font-semibold text-foreground mb-2">Compare Models</h3>
                  <p className="text-sm text-muted-foreground">
                    Compare specifications, prices, and features of different laptops
                  </p>
                </div>
                <div className="p-4 border rounded-xl bg-card hover:bg-accent/50 transition-colors">
                  <h3 className="font-semibold text-foreground mb-2">Get Recommendations</h3>
                  <p className="text-sm text-muted-foreground">
                    Get personalized suggestions based on your needs and budget
                  </p>
                </div>
                <div className="p-4 border rounded-xl bg-card hover:bg-accent/50 transition-colors">
                  <h3 className="font-semibold text-foreground mb-2">Technical Specs</h3>
                  <p className="text-sm text-muted-foreground">
                    Detailed information about processors, memory, storage, and more
                  </p>
                </div>
                <div className="p-4 border rounded-xl bg-card hover:bg-accent/50 transition-colors">
                  <h3 className="font-semibold text-foreground mb-2">Price Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    Compare prices and find the best deals across different retailers
                  </p>
                </div>
              </div>

              {/* Centered Message Input */}
              <div className="w-full max-w-2xl">
                <MessageInput
                  onSendMessage={sendMessage}
                  isLoading={isLoading}
                  placeholder="Ask me about laptops, compare models, or get recommendations..."
                  className="transition-all duration-500 ease-in-out"
                />
              </div>
            </div>
          </div>
        ) : (
          /* Chat Interface */
          <div className="flex-1 flex flex-col min-h-0">
            <MessageList messages={messages} isLoading={isLoading} />
            
            {/* Suggested Actions */}
            {suggestedActions.length > 0 && (
              <div className="border-t bg-muted/30 p-4">
                <SuggestedActions
                  actions={suggestedActions}
                  onActionClick={handleActionClick}
                />
              </div>
            )}

            {/* Message Input at Bottom */}
            <div className="transition-all duration-500 ease-in-out">
              <MessageInput
                onSendMessage={sendMessage}
                isLoading={isLoading}
                placeholder="Continue the conversation..."
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}