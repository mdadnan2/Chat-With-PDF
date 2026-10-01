"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { FileText, Menu, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DocumentList } from "@/components/chat/document-list";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { UserMenu } from "@/components/layout/user-menu";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import { useDocument } from "@/providers/document-provider";

function formatDocumentTitle(filename: string) {
    const title = filename
        .replace(/\.pdf$/i, "")
        .replace(/[_-]+/g, " ")
        .replace(/\s+/g, " ")
        .trim();
    return title || filename;
}

function DocumentsPanel({ onSelect }: { onSelect?: () => void }) {
    return (
        <div className="flex h-full min-h-0 flex-col">
            <div className="mb-3 flex items-center justify-between gap-3">
                <h2 className="text-xs font-semibold text-foreground">Documents</h2>
                <Button asChild variant="ghost" size="icon" className="h-8 w-8" aria-label="Upload document">
                    <Link href="/upload" onClick={onSelect}>
                        <Plus className="h-4 w-4" />
                    </Link>
                </Button>
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto">
                <DocumentList onSelect={onSelect} />
            </div>
            <p className="mt-3 border-t border-border/70 pt-3 text-[11px] text-muted-foreground">
                Your documents are private to your account.
            </p>
        </div>
    );
}

export function WorkspaceShell({ children }: { children: React.ReactNode }) {
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
    const { document } = useDocument();
    const pathname = usePathname();
    const isUpload = pathname === "/upload";

    return (
        <div className="flex h-dvh min-h-0 flex-col overflow-hidden bg-background">
            <header className="relative z-20 flex h-14 shrink-0 items-center justify-between gap-3 border-b border-border/70 bg-background px-3 sm:px-5">
                <div className="flex min-w-0 items-center gap-2.5">
                    <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="lg:hidden"
                        aria-label="Open documents"
                        aria-expanded={mobileSidebarOpen}
                        onClick={() => setMobileSidebarOpen(true)}
                    >
                        <Menu />
                    </Button>
                    <Link href="/chat" className="flex shrink-0 items-center gap-2.5 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                            <FileText className="h-4 w-4" />
                        </span>
                        <span className="hidden text-sm font-semibold tracking-tight sm:inline">Chat with PDF</span>
                    </Link>
                </div>

                {/* Absolutely centered over the full header width */}
                <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                    <span
                        className={isUpload
                            ? "text-sm font-semibold tracking-tight text-foreground"
                            : "max-w-sm truncate text-xs font-medium text-foreground/75"
                        }
                        title={!isUpload ? document?.name : undefined}
                        aria-label={isUpload ? "Add a document" : document?.name ?? "No document selected"}
                    >
                        {isUpload ? "Add a document" : document ? formatDocumentTitle(document.name) : "Choose a document to start"}
                    </span>
                </div>

                <div className="flex shrink-0 items-center gap-1">
                    <ThemeToggle />
                    <UserMenu />
                </div>
            </header>

            <div className="relative flex min-h-0 flex-1">
                <aside className="hidden w-60 shrink-0 border-r border-border/70 bg-muted/20 p-4 lg:block xl:w-64">
                    <DocumentsPanel />
                </aside>

                <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
                    {children}
                </main>
            </div>

            <Dialog open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
                <DialogContent className="left-0 top-0 h-[100dvh] w-[min(20rem,88vw)] max-w-none translate-x-0 translate-y-0 rounded-none border-y-0 border-l-0 p-5 data-[state=open]:slide-in-from-left data-[state=closed]:slide-out-to-left">
                    <DialogHeader className="sr-only">
                        <DialogTitle>Documents</DialogTitle>
                    </DialogHeader>
                    <DocumentsPanel onSelect={() => setMobileSidebarOpen(false)} />
                </DialogContent>
            </Dialog>
        </div>
    );
}
