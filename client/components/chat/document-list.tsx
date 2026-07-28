"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileText, Trash2, Loader2, Plus } from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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

export function DocumentList() {
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
  };

  const handleDelete = async () => {
    if (!pendingDelete) return;
    setIsDeleting(true);
    try {
      await deleteDoc(pendingDelete.id);
      toast.success("Document deleted");
      if (currentDoc?.id === pendingDelete.id) {
        setDocument(null);
        router.replace("/upload");
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
      <div className="flex flex-col items-center justify-center py-8 text-center px-2">
        <FileText className="h-8 w-8 text-muted-foreground/40 mb-2" />
        <p className="text-xs text-muted-foreground">No documents yet</p>
        <Button asChild variant="outline" size="sm" className="mt-3 gap-1.5">
          <Link href="/upload"><Plus className="h-3.5 w-3.5" />Upload</Link>
        </Button>
      </div>
    );
  }

  return (
    <>
      <div className="space-y-1.5">
        <AnimatePresence>
          {documents.map((doc) => {
            const isActive = currentDoc?.id === doc.id;
            return (
              <motion.div
                key={doc.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -8 }}
                className={`group relative flex items-start gap-2.5 rounded-xl border p-3 cursor-pointer transition-all ${
                  isActive
                    ? "border-primary/40 bg-primary/5"
                    : "border-transparent hover:border-border hover:bg-muted/50"
                }`}
                onClick={() => handleSelect(doc)}
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                  <FileText className="h-4 w-4 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-foreground truncate leading-tight">
                    {doc.original_filename}
                  </p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    {new Date(doc.uploaded_at).toLocaleDateString()}
                  </p>
                  {isActive && (
                    <Badge variant="success" className="mt-1 text-[10px] px-1.5 py-0">
                      Active
                    </Badge>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setPendingDelete(doc);
                  }}
                  className="opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive p-0.5 rounded"
                  aria-label="Delete document"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
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
