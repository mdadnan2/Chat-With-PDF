import Link from "next/link";
import { FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

const suggestions = [
  "Summarize this document",
  "Find the key risks",
  "Extract important requirements",
  "Verify a claim",
];

interface EmptyStateProps {
  onSuggestion: (text: string) => void;
  hasDocument: boolean;
}

export function EmptyState({ onSuggestion, hasDocument }: EmptyStateProps) {
  return (
    <div className="mx-auto flex h-full w-full max-w-2xl flex-col items-center justify-center px-4 py-12 text-center">
      <div className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl border border-border bg-card text-primary">
        <FileText className="h-5 w-5" />
      </div>
      <h2 className="text-xl font-semibold tracking-tight text-foreground">
        {hasDocument ? "Chat with your document" : "Upload a PDF to begin"}
      </h2>
      <p className="mt-2 max-w-sm text-sm leading-relaxed text-muted-foreground">
        {hasDocument
          ? "Ask a question and get an answer grounded in this document."
          : "Choose a document from the sidebar or upload one to start a conversation."}
      </p>
      {!hasDocument ? (
        <Button asChild className="mt-5 gap-2">
          <Link href="/upload">Upload PDF</Link>
        </Button>
      ) : (
        <div className="mt-7 flex max-w-xl flex-wrap justify-center gap-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => onSuggestion(suggestion)}
              className="rounded-full border border-border bg-background px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              {suggestion}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
