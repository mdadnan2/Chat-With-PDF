import { Navbar } from "@/components/layout/navbar";
import { UploadZone } from "@/components/upload/upload-zone";
import { FileText, ShieldCheck, Zap, Lock } from "lucide-react";

export const metadata = {
  title: "Upload PDF — PDFChat",
  description: "Upload your PDF document to start chatting with AI.",
};

const trustItems = [
  { icon: ShieldCheck, label: "PDF only · Max 50MB" },
  { icon: Zap, label: "Processed in seconds" },
  { icon: Lock, label: "Secure & private" },
];

export default function UploadPage() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <Navbar />
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16">
        {/* Header */}
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
            Our AI will read, understand, and index your document so you can
            ask questions and get instant answers.
          </p>
        </div>

        {/* Upload zone */}
        <UploadZone />

        {/* Trust indicators */}
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
