"use client";

import { useRef } from "react";
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
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !isLoading && value.trim()) {
      if (e.shiftKey) return;
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex items-end gap-2 rounded-xl border border-border bg-background p-2 shadow-sm transition-shadow focus-within:ring-2 focus-within:ring-ring/40">
      <Textarea
        ref={inputRef}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={Math.min(5, Math.max(1, value.split("\n").length))}
        placeholder="Ask a question about this document..."
        disabled={disabled || isLoading}
        className="min-h-10 max-h-36 flex-1 border-0 bg-transparent px-2 py-2 text-sm shadow-none focus-visible:ring-0 disabled:cursor-not-allowed"
        aria-label="Chat message input"
      />
      <Button
        onClick={onSubmit}
        disabled={!value.trim() || isLoading || disabled}
        size="icon"
        className={cn("mb-0.5 h-9 w-9 shrink-0 rounded-lg", !value.trim() && "opacity-50")}
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
