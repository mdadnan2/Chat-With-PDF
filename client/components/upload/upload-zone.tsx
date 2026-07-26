"use client";

import { useCallback, useState } from "react";
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

export function UploadZone() {
  const router = useRouter();
  const { setDocument } = useDocument();
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
  };

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");
    setProgress(0);

    try {
      const response = await uploadService.uploadPDF(file, setProgress);
      setStatus("success");
      setDocument({
        id: response.data.id,
        name: response.data.original_name,
        size: response.data.size,
        uploadedAt: response.data.uploaded_at,
      });
      toast.success("PDF uploaded successfully!");
      setTimeout(() => router.push("/chat"), 800);
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
    <div className="w-full max-w-xl mx-auto space-y-4">
      <AnimatePresence mode="wait">
        {!file ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={onDrop}
            className={cn(
              "relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200 cursor-pointer",
              isDragging
                ? "border-primary bg-primary/5 scale-[1.01]"
                : "border-border hover:border-primary/50 hover:bg-muted/50"
            )}
            onClick={() => document.getElementById("file-input")?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={onInputChange}
            />
            <div className={cn(
              "mb-4 flex h-16 w-16 items-center justify-center rounded-2xl transition-colors",
              isDragging ? "bg-primary/20" : "bg-muted"
            )}>
              <Upload className={cn("h-7 w-7 transition-colors", isDragging ? "text-primary" : "text-muted-foreground")} />
            </div>
            <p className="font-semibold text-foreground mb-1">
              {isDragging ? "Drop your PDF here" : "Drag & drop your PDF"}
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              or click to browse files
            </p>
            <p className="text-xs text-muted-foreground">PDF only · Max 50MB</p>
          </motion.div>
        ) : (
          <motion.div
            key="file-preview"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="rounded-2xl border border-border bg-card p-6 space-y-4"
          >
            <div className="flex items-start gap-4">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary/10">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground truncate">{file.name}</p>
                <p className="text-sm text-muted-foreground mt-0.5">{formatFileSize(file.size)}</p>
              </div>
              {status === "idle" && (
                <button
                  onClick={removeFile}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label="Remove file"
                >
                  <X className="h-4 w-4" />
                </button>
              )}
              {status === "success" && <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />}
              {status === "error" && <AlertCircle className="h-5 w-5 text-destructive shrink-0" />}
            </div>

            {status === "uploading" && (
              <div className="space-y-2">
                <Progress value={progress} />
                <p className="text-xs text-muted-foreground text-right">{progress}%</p>
              </div>
            )}

            {error && (
              <p className="text-sm text-destructive flex items-center gap-1.5">
                <AlertCircle className="h-3.5 w-3.5" /> {error}
              </p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {file && status !== "success" && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Button
            onClick={handleUpload}
            disabled={status === "uploading"}
            className="w-full"
            size="lg"
          >
            {status === "uploading" ? (
              <>
                <span className="h-4 w-4 rounded-full border-2 border-primary-foreground/30 border-t-primary-foreground animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4" />
                Upload & Start Chatting
              </>
            )}
          </Button>
        </motion.div>
      )}
    </div>
  );
}
