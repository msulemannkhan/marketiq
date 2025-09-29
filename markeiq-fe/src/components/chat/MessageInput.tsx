"use client";

import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Loader } from '@/lib/components';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  placeholder?: string;
  className?: string;
}

export function MessageInput({ 
  onSendMessage, 
  isLoading, 
  placeholder = "Ask about laptops, compare models, or get recommendations...",
  className 
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
      resetTextareaHeight();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const resetTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const adjustTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const minHeight = 52; // Minimum height in pixels
      const maxHeight = 200; // Maximum height in pixels
      const newHeight = Math.max(minHeight, Math.min(scrollHeight, maxHeight));
      textareaRef.current.style.height = `${newHeight}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  return (
    <div className={cn("border-t bg-background p-4", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isLoading}
            className={cn(
              "w-full resize-none rounded-2xl border border-input bg-background px-4 py-3 pr-14",
              "text-sm placeholder:text-muted-foreground",
              "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
              "disabled:cursor-not-allowed disabled:opacity-50",
              "min-h-[52px] max-h-[200px] transition-all duration-200",
              "shadow-sm hover:shadow-md focus:shadow-lg",
              "overflow-y-auto scrollbar-thin scrollbar-thumb-[#595959] scrollbar-track-transparent"
            )}
            style={{ height: 'auto' }}
          />
          {/* Send Button Inside Textarea */}
          <Button
            type="submit"
            disabled={!message.trim() || isLoading}
            size="icon"
            className={cn(
              "absolute right-3 bottom-0 -translate-y-1/2 h-8 w-8 rounded-xl",
              "bg-primary hover:bg-primary/90 text-primary-foreground",
              "transition-all duration-200 hover:scale-105",
              "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
              "shadow-sm hover:shadow-md",
              message.trim() && !isLoading 
                ? "animate-pulse" 
                : "animate-none"
            )}
          >
            {isLoading ? (
              <Loader />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
      
      <div className="mt-3 text-xs text-muted-foreground text-center">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}
