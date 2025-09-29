"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "@/types/chat";
import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { ProductDetails } from "@/components/chat/ProductDetails";
import { Citations } from "@/components/chat/Citations";
import { Recommendations } from "@/components/chat/Recommendations";
import { MarkdownRenderer } from "@/components/chat/MarkdownRenderer";
import { Loader } from "@/lib/components";

interface MessageListProps {
    messages: ChatMessage[];
    isLoading: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    if (messages.length === 0) {
        return (
            <div className="flex-1 flex items-center justify-center p-8">
                <div className="text-center max-w-md mx-auto">
                    <div className="w-16 h-16 mx-auto mb-4 bg-primary/10 rounded-full flex items-center justify-center">
                        <Bot className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="text-xl font-semibold text-foreground mb-2">
                        AI Assistant
                    </h3>
                    <p className="text-muted-foreground">
                        Get personalized laptop recommendations powered by AI.
                        Ask questions about business laptops, compare models,
                        and get expert advice.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages
                .filter((message) => !message.isTyping) // Filter out messages that are just typing indicators
                .map((message) => (
                    <div
                        key={message.id}
                        className={cn(
                            "flex gap-4",
                            message.role === "user"
                                ? "justify-end"
                                : "justify-start"
                        )}
                    >
                        {message.role === "assistant" && (
                            <div className="p-2 h-fit bg-primary/10 dark:bg-gradient-to-br dark:from-white/15 dark:to-white/10 dark:backdrop-blur-md rounded-xl border border-primary/20 dark:border-white/20 shadow-lg">
                                <Bot className="h-6 w-6 text-primary dark:text-white" />
                            </div>
                        )}

                        <div
                            className={cn(
                                "max-w-[80%] rounded-2xl px-4 py-3",
                                message.role === "user"
                                    ? "bg-primary text-primary-foreground ml-12"
                                    : "bg-muted mr-12"
                            )}
                        >
                            <MarkdownRenderer content={message.content} />

                            {message.products_mentioned &&
                                message.products_mentioned.length > 0 && (
                                    <div className="mt-4">
                                        <ProductDetails
                                            products={
                                                message.products_mentioned
                                            }
                                        />
                                    </div>
                                )}

                            {message.recommendations &&
                                message.recommendations.length > 0 && (
                                    <div className="mt-4">
                                        <Recommendations
                                            recommendations={message.recommendations}
                                        />
                                    </div>
                                )}

                            {message.citations &&
                                message.citations.length > 0 && (
                                    <div className="mt-4">
                                        <Citations
                                            citations={message.citations}
                                        />
                                    </div>
                                )}
                        </div>

                        {message.role === "user" && (
                            <div className="p-2 h-fit bg-primary/10 dark:bg-gradient-to-br dark:from-white/15 dark:to-white/10 dark:backdrop-blur-md rounded-xl border border-primary/20 dark:border-white/20 shadow-lg">
                                <User className="h-6 w-6 text-primary dark:text-white" />
                            </div>
                        )}
                    </div>
                ))}

            {isLoading && (
                <div className="flex gap-4 justify-start">
                    <div className="p-2 h-fit bg-primary/10 dark:bg-gradient-to-br dark:from-white/15 dark:to-white/10 dark:backdrop-blur-md rounded-xl border border-primary/20 dark:border-white/20 shadow-lg">
                        <Bot className="h-6 w-6 text-primary dark:text-white" />
                    </div>
                    <div className="bg-muted rounded-2xl px-4 py-3 mr-12">
                        <div className="flex items-center gap-2">
                            <Loader />
                            <span className="text-muted-foreground">
                                AI is thinking...
                            </span>
                        </div>
                    </div>
                </div>
            )}

            <div ref={messagesEndRef} />
        </div>
    );
}
