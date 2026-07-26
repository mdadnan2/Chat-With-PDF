"use client";

import { useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ value, onChange, onSubmit, isLoading, disabled }: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  // Auto-focus on mount
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isLoading && value.trim()) onSubmit();
    }
  };

  return (
    <div className="relative flex items-end gap-2 rounded-xl border border-border bg-background p-2 shadow-sm focus-within:ring-1 focus-within:ring-ring transition-shadow">
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about your document..."
        disabled={disabled || isLoading}
        className="min-h-[44px] max-h-[160px] border-0 shadow-none focus-visible:ring-0 resize-none py-2.5 px-2"
        aria-label="Chat message input"
      />
      <Button
        onClick={onSubmit}
        disabled={!value.trim() || isLoading || disabled}
        size="icon"
        className={cn("shrink-0 h-9 w-9 rounded-lg transition-all", !value.trim() && "opacity-50")}
        aria-label="Send message"
      >
        {isLoading ? (
          <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
        ) : (
          <Send className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}
