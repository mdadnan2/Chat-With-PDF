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
      <section className="flex min-h-0 flex-1 flex-col overflow-y-auto px-4 py-6 sm:px-6 sm:py-8">
        <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center">
          <div className="mb-8">
            <Button asChild variant="ghost" size="sm" className="-ml-2 gap-2 text-muted-foreground">
              <Link href="/chat">
                <ArrowLeft className="h-4 w-4" /> Back to chat
              </Link>
            </Button>
          </div>
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">Add a document</h1>
            <p className="mt-2 text-sm text-muted-foreground">Upload a PDF to get started.</p>
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
