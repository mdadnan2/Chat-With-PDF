"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrainCircuit, FileText, Menu, MessageSquare, Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { DocumentList } from "@/components/chat/document-list";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { UserMenu } from "@/components/layout/user-menu";
import { cn } from "@/lib/utils";

export function WorkspaceShell({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

    const routeLinkClass = (active: boolean) =>
        cn(
            "flex h-10 items-center gap-3 rounded-md border px-3 text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
            active
                ? "border-primary/20 bg-primary/10 font-semibold text-primary"
                : "border-transparent font-medium text-muted-foreground hover:bg-accent hover:text-foreground"
        );

    return (
        <div className="flex h-dvh min-h-0 flex-col overflow-hidden bg-background">
            <header className="flex h-14 shrink-0 items-center justify-between gap-2 border-b border-border/50 bg-background/90 px-3 sm:px-4">
                <div className="flex min-w-0 items-center gap-2">
                    <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="shrink-0 lg:hidden"
                        aria-label={mobileSidebarOpen ? "Close documents" : "Open documents"}
                        aria-expanded={mobileSidebarOpen}
                        onClick={() => setMobileSidebarOpen((open) => !open)}
                    >
                        {mobileSidebarOpen ? <X /> : <Menu />}
                    </Button>
                    <Link href="/" className="flex shrink-0 items-center gap-2 group">
                        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                            <FileText className="h-3.5 w-3.5 text-primary" />
                        </span>
                        <span className="hidden font-semibold text-sm sm:inline">
                            PDF<span className="text-primary">Chat</span>
                        </span>
                    </Link>
                </div>

                <div className="flex shrink-0 items-center gap-1 sm:gap-2">
                    <ThemeToggle />
                    <UserMenu />
                </div>
            </header>

            <div className="relative flex min-h-0 flex-1">
                {mobileSidebarOpen && (
                    <button
                        type="button"
                        className="absolute inset-0 z-30 bg-black/40 lg:hidden"
                        aria-label="Close documents panel"
                        onClick={() => setMobileSidebarOpen(false)}
                    />
                )}

                <aside
                    className={cn(
                        "z-40 min-h-0 shrink-0 flex-col border-r border-border/50 bg-background p-4",
                        mobileSidebarOpen
                            ? "absolute inset-y-0 left-0 flex w-[min(18rem,85vw)] shadow-xl lg:relative lg:inset-auto lg:w-72 lg:shadow-none"
                            : "hidden lg:relative lg:flex lg:w-72"
                    )}
                >
                    <div className="mb-5 shrink-0">
                        <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                            Workspace
                        </p>
                        <nav aria-label="Workspace" className="space-y-1">
                            <Link
                                href="/chat"
                                aria-current={pathname === "/chat" ? "page" : undefined}
                                className={routeLinkClass(pathname === "/chat")}
                                onClick={() => setMobileSidebarOpen(false)}
                            >
                                <MessageSquare className="h-4 w-4 shrink-0" />
                                <span>Chat</span>
                                {pathname === "/chat" && <span className="ml-auto text-[10px] uppercase tracking-wider">Open</span>}
                            </Link>
                            <Link
                                href="/agents"
                                aria-current={pathname === "/agents" ? "page" : undefined}
                                className={routeLinkClass(pathname === "/agents")}
                                onClick={() => setMobileSidebarOpen(false)}
                            >
                                <BrainCircuit className="h-4 w-4 shrink-0" />
                                <span>AI Agents</span>
                                {pathname === "/agents" && <span className="ml-auto text-[10px] uppercase tracking-wider">Open</span>}
                            </Link>
                        </nav>
                    </div>

                    <div className="mb-3 flex shrink-0 items-center justify-between">
                        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Documents</p>
                        <Button asChild variant="ghost" size="icon" className="h-7 w-7" aria-label="Upload new document">
                            <Link href="/upload"><Plus className="h-3.5 w-3.5" /></Link>
                        </Button>
                    </div>
                    <div className="min-h-0 flex-1 overflow-y-auto">
                        <DocumentList onSelect={() => setMobileSidebarOpen(false)} />
                    </div>
                </aside>

                <main className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
                    {children}
                </main>
            </div>
        </div>
    );
}