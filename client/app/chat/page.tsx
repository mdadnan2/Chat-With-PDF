"use client";

import { motion } from "framer-motion";
import { ChatInterface } from "@/components/chat/chat-interface";
import { DocumentList } from "@/components/chat/document-list";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { UserMenu } from "@/components/layout/user-menu";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { FileText, Plus } from "lucide-react";
import Link from "next/link";

function ChatPageContent() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background">
      {/* Top bar */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-border/50 bg-background/80 backdrop-blur-xl px-4">
        <Link href="/" className="flex items-center gap-2 group">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
            <FileText className="h-3.5 w-3.5 text-primary" />
          </div>
          <span className="font-semibold text-sm">
            PDF<span className="text-primary">Chat</span>
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <UserMenu />
        </div>
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <motion.aside
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="hidden w-72 shrink-0 overflow-y-auto border-r border-border/50 p-4 lg:flex lg:flex-col gap-4"
        >
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Documents
            </p>
            <Button asChild variant="ghost" size="icon" className="h-7 w-7">
              <Link href="/upload" aria-label="Upload new document">
                <Plus className="h-3.5 w-3.5" />
              </Link>
            </Button>
          </div>
          <DocumentList />
        </motion.aside>

        {/* Chat area */}
        <motion.main
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="flex flex-1 flex-col overflow-hidden"
        >
          <ChatInterface />
        </motion.main>
      </div>
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}
