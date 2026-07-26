"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ChatInterface } from "@/components/chat/chat-interface";
import { DocumentCard } from "@/components/chat/document-card";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { useDocument } from "@/providers/document-provider";
import { FileText } from "lucide-react";
import Link from "next/link";

export default function ChatPage() {
  const router = useRouter();
  const { document } = useDocument();

  useEffect(() => {
    if (!document) router.replace("/upload");
  }, [document, router]);

  if (!document) return null;

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
        <ThemeToggle />
      </header>

      {/* Main layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <motion.aside
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="hidden w-72 shrink-0 overflow-y-auto border-r border-border/50 p-4 lg:block"
        >
          <DocumentCard document={document} />
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
