"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Trash2, Loader2, Plus, Check } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useDocuments, useDeleteDocument } from "@/hooks";
import { useDocument } from "@/providers/document-provider";
import type { Document } from "@/types";
import Link from "next/link";

export function DocumentList({ onSelect }: { onSelect?: () => void }) {
  const router = useRouter();
  const { document: currentDoc, setDocument } = useDocument();
  const { data: documents, isLoading } = useDocuments();
  const { mutateAsync: deleteDoc } = useDeleteDocument();
  const [pendingDelete, setPendingDelete] = useState<Document | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleSelect = (doc: Document) => {
    setDocument({
      id: doc.id,
      name: doc.original_filename,
      size: 0,
      uploadedAt: doc.uploaded_at,
    });
    onSelect?.();
  };

  const handleDelete = async () => {
    if (!pendingDelete) return;
    setIsDeleting(true);
    try {
      await deleteDoc(pendingDelete.id);
      toast.success("Document deleted");
      if (currentDoc?.id === pendingDelete.id) {
        setDocument(null);
        router.replace("/chat");
      }
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Failed to delete document");
    } finally {
      setIsDeleting(false);
      setPendingDelete(null);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-2 p-1">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-16 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (!documents?.length) {
    return (
      <div className="space-y-3 px-2 py-4">
        <p className="text-xs leading-relaxed text-muted-foreground">Upload a PDF to start a conversation.</p>
        <Button asChild variant="outline" size="sm" className="w-full gap-1.5">
          <Link href="/upload"><Plus className="h-3.5 w-3.5" />Upload PDF</Link>
        </Button>
      </div>
    );
  }

  return (
    <>
      <div role="list" className="space-y-1">
        {documents.map((doc) => {
          const isActive = currentDoc?.id === doc.id;
          return (
            <div key={doc.id} role="listitem" className="group flex items-center gap-1">
              <button
                type="button"
                onClick={() => handleSelect(doc)}
                aria-current={isActive ? "true" : undefined}
                className={`flex min-w-0 flex-1 items-center gap-2.5 rounded-md px-2.5 py-2 text-left transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring ${isActive
                  ? "bg-primary/10 text-foreground"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }`}
              >
                <FileText className="h-4 w-4 shrink-0" />
                <span className="min-w-0 flex-1 truncate text-xs font-medium" title={doc.original_filename}>{doc.original_filename}</span>
                {isActive && <Check className="h-3.5 w-3.5 shrink-0 text-primary" />}
              </button>
              <button
                type="button"
                onClick={() => setPendingDelete(doc)}
                className="rounded p-2 text-muted-foreground opacity-100 transition-colors hover:text-destructive focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring lg:opacity-0 lg:group-hover:opacity-100"
                aria-label={`Delete ${doc.original_filename}`}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          );
        })}
      </div>

      <Dialog open={!!pendingDelete} onOpenChange={(open) => !open && setPendingDelete(null)}>
        <DialogContent className="max-w-sm">
          <DialogHeader>
            <DialogTitle>Delete document?</DialogTitle>
            <DialogDescription>
              &ldquo;{pendingDelete?.original_filename}&rdquo; will be permanently deleted. This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" onClick={() => setPendingDelete(null)} disabled={isDeleting}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={isDeleting}>
              {isDeleting ? <><Loader2 className="h-4 w-4 animate-spin" /> Deleting...</> : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
