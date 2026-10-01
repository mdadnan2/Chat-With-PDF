"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { toast } from "sonner";
import { MessageBubble } from "./message-bubble";
import { ChatInput } from "./chat-input";
import { TypingIndicator } from "./typing-indicator";
import { EmptyState } from "./empty-state";
import { agentService } from "@/services/api";
import { useDocument } from "@/providers/document-provider";
import { generateId } from "@/lib/utils";
import type { Message } from "@/types";

export function ChatInterface() {
  const { document } = useDocument();
  return <ChatSession key={document?.id ?? "no-document"} document={document} />;
}

function ChatSession({ document }: { document: ReturnType<typeof useDocument>["document"] }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  const sendMessage = async () => {
    const question = input.trim();
    if (!question || isLoading || !document) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setError(null);
    setIsLoading(true);

    try {
      const response = await agentService.run({
        document_id: document.id,
        question,
      });
      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        summary: response.summary,
        findings: response.findings,
        activity: response.activity,
        agent: response.agent,
        routing: response.routing,
        verification: response.verification,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to get response";
      setError(message);
      toast.error(message);
      setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));
      setInput(question);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
        {messages.length === 0 ? (
          <EmptyState
            onSuggestion={(text) => setInput(text)}
            hasDocument={Boolean(document)}
          />
        ) : (
          <div className="mx-auto w-full max-w-3xl space-y-8">
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
            {isLoading && <TypingIndicator />}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="shrink-0 bg-background/95 px-4 pb-4 pt-3 sm:px-6 sm:pb-5 lg:px-8">
        <div className="mx-auto w-full max-w-3xl">
          {error && (
            <p role="alert" className="mb-2 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
              {error} Your question is still in the composer; try again when you’re ready.
            </p>
          )}
          <ChatInput
            value={input}
            onChange={setInput}
            onSubmit={sendMessage}
            isLoading={isLoading}
            disabled={!document}
          />
          <p className="mt-2 text-center text-[10px] text-muted-foreground">
            Answers are generated from the selected document.
          </p>
        </div>
      </div>
    </div>
  );
}
