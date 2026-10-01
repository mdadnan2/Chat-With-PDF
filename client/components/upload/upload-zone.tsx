"use client";

import { useCallback, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, X, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { cn, formatFileSize } from "@/lib/utils";
import { uploadService } from "@/services/api";
import { useDocument } from "@/providers/document-provider";

const MAX_SIZE = 50 * 1024 * 1024; // 50MB

export function UploadZone({ className }: { className?: string }) {
  const router = useRouter();
  const { setDocument } = useDocument();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  const validateFile = (f: File): string | null => {
    if (f.type !== "application/pdf") return "Only PDF files are supported.";
    if (f.size > MAX_SIZE) return `File too large. Maximum size is ${formatFileSize(MAX_SIZE)}.`;
    return null;
  };

  const handleFile = useCallback((f: File) => {
    const err = validateFile(f);
    if (err) {
      setError(err);
      toast.error(err);
      return;
    }
    setFile(f);
    setError(null);
    setStatus("idle");
    setProgress(0);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const dropped = e.dataTransfer.files[0];
      if (dropped) handleFile(dropped);
    },
    [handleFile]
  );

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
    e.target.value = "";
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setProgress(0);

    try {
      const response = await uploadService.uploadPDF(file, setProgress);
      sessionStorage.removeItem("showUpload");
      setDocument({
        id: response.data.id,
        name: response.data.original_name,
        size: response.data.size,
        uploadedAt: response.data.uploaded_at,
      });
      setStatus("success");
      toast.success("PDF uploaded successfully!");
      window.setTimeout(() => router.push("/chat"), 900);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setStatus("error");
      setError(message);
      toast.error(message);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
    setStatus("idle");
    setProgress(0);
  };

  return (
    <div className={cn("mx-auto w-full space-y-3", className)}>
      <input
        ref={fileInputRef}
        id="file-input"
        type="file"
        accept=".pdf,application/pdf"
        className="sr-only"
        tabIndex={-1}
        aria-hidden="true"
        onChange={onInputChange}
      />
      <AnimatePresence mode="wait">
        {!file ? (
          <motion.button
            type="button"
            key="dropzone"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            onClick={() => fileInputRef.current?.click()}
            className={cn(
              "w-full flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-8 text-center font-sans transition-all duration-200 cursor-pointer sm:py-10",
              isDragging
                ? "border-primary bg-primary/5 scale-[1.01]"
                : "border-border bg-card hover:border-primary/60 hover:bg-muted/30",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            )}
          >
            <div className={cn(
              "mb-4 flex h-14 w-14 items-center justify-center rounded-xl transition-colors duration-200",
              isDragging ? "bg-primary/20" : "bg-muted"
            )}>
              <Upload className={cn("h-6 w-6 transition-colors duration-200", isDragging ? "text-primary" : "text-muted-foreground")} />
            </div>
            <p className="text-base font-semibold text-foreground">
              {isDragging ? "Drop your PDF here" : "Drag & drop your PDF"}
            </p>
            <p className="mt-1 text-sm text-muted-foreground">or click to browse files</p>
            <span className="mt-5 inline-flex items-center rounded-full border border-border bg-muted/60 px-3 py-1 text-xs text-muted-foreground">
              PDF only · Max 50 MB
            </span>
          </motion.button>
        ) : (
          <motion.div
            key="file-preview"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className={cn(
              "rounded-2xl border bg-card p-5 space-y-4 transition-colors",
              status === "error" ? "border-destructive/50" : status === "success" ? "border-emerald-500/40" : "border-border"
            )}
          >
            <div className="flex items-center gap-3">
              <div className={cn(
                "flex h-11 w-11 shrink-0 items-center justify-center rounded-xl transition-colors",
                status === "success" ? "bg-emerald-500/10" : status === "error" ? "bg-destructive/10" : "bg-primary/10"
              )}>
                {status === "success"
                  ? <CheckCircle2 className="h-5 w-5 text-emerald-500" />
                  : status === "error"
                  ? <AlertCircle className="h-5 w-5 text-destructive" />
                  : <FileText className="h-5 w-5 text-primary" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="truncate text-sm font-medium text-foreground" title={file.name}>{file.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{formatFileSize(file.size)}</p>
              </div>
              {status !== "uploading" && status !== "success" && (
                <button
                  type="button"
                  onClick={removeFile}
                  className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  aria-label="Remove file"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
            </div>

            {status === "uploading" && (
              <div className="space-y-1.5" role="status" aria-live="polite">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Uploading…</span>
                  <span>{Math.min(progress, 99)}%</span>
                </div>
                <Progress value={Math.min(progress, 99)} aria-label="Upload progress" />
              </div>
            )}

            {status === "success" && (
              <p className="text-sm font-medium text-emerald-600 dark:text-emerald-400" role="status" aria-live="polite">
                Upload complete — opening your chat…
              </p>
            )}

            {error && status === "error" && (
              <p role="alert" className="text-sm text-destructive">{error}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {file && status !== "success" && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}>
          <Button
            onClick={handleUpload}
            disabled={status === "uploading"}
            className="w-full"
            size="lg"
          >
            {status === "uploading" ? (
              <>
                <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
                Uploading…
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                {status === "error" ? "Try Again" : "Upload & Start Chatting"}
              </>
            )}
          </Button>
        </motion.div>
      )}
    </div>
  );
}
