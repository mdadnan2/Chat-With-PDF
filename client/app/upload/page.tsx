"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { UploadZone } from "@/components/upload/upload-zone";
import { WorkspaceShell } from "@/components/layout/workspace-shell";
import { ProtectedRoute } from "@/components/auth/protected-route";

function UploadPageContent() {
  return (
    <WorkspaceShell>
      <section className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        {/* Back to chat — left-aligned, consistent inset */}
        <div className="px-4 pt-5 sm:px-8 sm:pt-6">
          <Button asChild variant="ghost" size="sm" className="-ml-2 gap-2 text-muted-foreground">
            <Link href="/chat">
              <ArrowLeft className="h-4 w-4" /> Back to chat
            </Link>
          </Button>
        </div>

        {/* Centered content column */}
        <div className="mx-auto w-full max-w-md px-4 pb-10 pt-6 sm:px-6">
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Add a document</h1>
            <p className="mt-1.5 text-sm text-muted-foreground">Upload a PDF to start chatting with it.</p>
          </div>
          <UploadZone className="max-w-none" />
        </div>
      </section>
    </WorkspaceShell>
  );
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadPageContent />
    </ProtectedRoute>
  );
}
