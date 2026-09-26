"use client";

import { ChatInterface } from "@/components/chat/chat-interface";
import { WorkspaceShell } from "@/components/layout/workspace-shell";
import { ProtectedRoute } from "@/components/auth/protected-route";

function ChatPageContent() {
  return (
    <WorkspaceShell>
      <ChatInterface />
    </WorkspaceShell>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatPageContent />
    </ProtectedRoute>
  );
}
