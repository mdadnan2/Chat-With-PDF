"use client";

import { useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  disabled?: boolean;
}

export function ChatInput({ value, onChange, onSubmit, isLoading, disabled }: ChatInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !isLoading && value.trim()) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="relative flex items-center gap-2 rounded-xl border border-border bg-background px-3 py-2 shadow-sm focus-within:ring-1 focus-within:ring-ring transition-shadow">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask anything about your document..."
        disabled={disabled || isLoading}
        className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
        aria-label="Chat message input"
      />
      <Button
        onClick={onSubmit}
        disabled={!value.trim() || isLoading || disabled}
        size="icon"
        className={cn("shrink-0 h-8 w-8 rounded-lg transition-all", !value.trim() && "opacity-50")}
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
