"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { TypingIndicator } from "./typing-indicator";
import { EmptyState } from "./empty-state";
import { chatService } from "@/services/api";
import { generateId } from "@/lib/utils";
import type { Message } from "@/types";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const sendMessage = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({ question });
      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to get response";
      toast.error(message);
      // Remove the user message on failure so they can retry
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      setInput(question);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        {messages.length === 0 ? (
          <EmptyState onSuggestion={(text) => setInput(text)} />
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-4">
        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={sendMessage}
          isLoading={isLoading}
        />
        <p className="text-center text-[11px] text-muted-foreground mt-2">
          Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
