import Link from "next/link";
import { FileText } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border/50 bg-background">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-6 sm:flex-row">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10">
              <FileText className="h-3.5 w-3.5 text-primary" />
            </div>
            <span className="font-semibold text-sm">
              PDF<span className="text-primary">Chat</span>
            </span>
          </Link>

          <p className="text-xs text-muted-foreground text-center">
            Built with Next.js, FastAPI & Gemini AI. Ask anything about your documents.
          </p>

          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} PDFChat
          </p>
        </div>
      </div>
    </footer>
  );
}
