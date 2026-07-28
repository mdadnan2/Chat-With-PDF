"use client";

import { useRouter } from "next/navigation";
import { FileText, ShieldCheck, Zap, Lock, MessageSquare, Upload as UploadIcon, Clock } from "lucide-react";
import { Navbar } from "@/components/layout/navbar";
import { UploadZone } from "@/components/upload/upload-zone";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useDocuments } from "@/hooks";
import { useDocument } from "@/providers/document-provider";
import { useState } from "react";

const trustItems = [
  { icon: ShieldCheck, label: "PDF only · Max 50MB" },
  { icon: Zap, label: "Processed in seconds" },
  { icon: Lock, label: "Secure & private" },
];

function RecentDocuments() {
  const router = useRouter();
  const { data: documents, isLoading } = useDocuments();
  const { document: currentDoc, setDocument } = useDocument();
  const [showUpload, setShowUpload] = useState(() => {
    if (typeof window !== "undefined") return sessionStorage.getItem("showUpload") === "true";
    return false;
  });

  if (isLoading) {
    return (
      <div className="w-full max-w-xl space-y-2">
        <Skeleton className="h-5 w-32" />
        {[1, 2].map((i) => <Skeleton key={i} className="h-16 w-full rounded-xl" />)}
      </div>
    );
  }

  if (!documents?.length || showUpload) {
    return <UploadZone />;
  }

  const handleContinue = () => {
    if (!currentDoc && documents[0]) {
      setDocument({
        id: documents[0].id,
        name: documents[0].original_filename,
        size: 0,
        uploadedAt: documents[0].uploaded_at,
      });
    }
    router.push("/chat");
  };

  return (
    <div className="w-full max-w-xl space-y-6">
      {/* Recent documents */}
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-muted-foreground" />
          <p className="text-sm font-medium text-muted-foreground">Recent Documents</p>
        </div>
        <div className="space-y-2">
          {documents.slice(0, 5).map((doc) => {
            const isActive = currentDoc?.id === doc.id;
            return (
              <button
                key={doc.id}
                onClick={() => {
                  setDocument({
                    id: doc.id,
                    name: doc.original_filename,
                    size: 0,
                    uploadedAt: doc.uploaded_at,
                  });
                  router.push("/chat");
                }}
                className={`w-full flex items-center gap-3 rounded-xl border p-3 text-left transition-all hover:border-primary/40 hover:bg-primary/5 ${
                  isActive ? "border-primary/40 bg-primary/5" : "border-border bg-card"
                }`}
              >
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <FileText className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">{doc.original_filename}</p>
                  <p className="text-xs text-muted-foreground">{doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : ""}</p>
                </div>
                {isActive && <Badge variant="success" className="shrink-0">Active</Badge>}
              </button>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Button onClick={handleContinue} className="flex-1 gap-2">
          <MessageSquare className="h-4 w-4" />
          Continue Chatting
        </Button>
        <Button variant="outline" onClick={() => { setShowUpload(true); sessionStorage.setItem("showUpload", "true"); }} className="flex-1 gap-2">
          <UploadIcon className="h-4 w-4" />
          Upload Another
        </Button>
      </div>
    </div>
  );
}

function UploadPageContent() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        <div className="w-full max-w-xl text-center mb-10">
          <div className="relative inline-flex mb-6">
            <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10 border border-primary/20 shadow-xl shadow-primary/10">
              <FileText className="h-9 w-9 text-primary" />
            </div>
            <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 shadow-md">
              <span className="text-[9px] font-bold text-white">AI</span>
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground mb-3">
            Upload your PDF
          </h1>
          <p className="text-muted-foreground leading-relaxed">
            Our AI will read, understand, and index your document so you can ask questions and get instant answers.
          </p>
        </div>

        <RecentDocuments />

        <div className="mt-8 flex flex-wrap items-center justify-center gap-6">
          {trustItems.map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Icon className="h-3.5 w-3.5 text-primary/70" />
              {label}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default function UploadPage() {
  return (
    <ProtectedRoute>
      <UploadPageContent />
    </ProtectedRoute>
  );
}
