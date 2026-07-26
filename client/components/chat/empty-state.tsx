import { Sparkles } from "lucide-react";

const suggestions = [
  "What is the main topic of this document?",
  "Summarize the key findings",
  "What are the most important points?",
  "List the conclusions mentioned",
];

interface EmptyStateProps {
  onSuggestion: (text: string) => void;
}

export function EmptyState({ onSuggestion }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full py-16 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 mb-6">
        <Sparkles className="h-8 w-8 text-primary" />
      </div>
      <h3 className="font-semibold text-foreground text-lg mb-2">
        Ready to answer your questions
      </h3>
      <p className="text-sm text-muted-foreground mb-8 max-w-sm">
        Ask anything about your document. I'll find the most relevant information and give you a precise answer.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
        {suggestions.map((s) => (
          <button
            key={s}
            onClick={() => onSuggestion(s)}
            className="rounded-xl border border-border bg-muted/50 px-4 py-3 text-sm text-muted-foreground hover:bg-muted hover:text-foreground hover:border-primary/30 transition-all text-left"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
