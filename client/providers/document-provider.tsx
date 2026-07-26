"use client";

import { createContext, useContext, useState } from "react";
import type { DocumentInfo } from "@/types";

interface DocumentContextValue {
  document: DocumentInfo | null;
  setDocument: (doc: DocumentInfo | null) => void;
}

const DocumentContext = createContext<DocumentContextValue | null>(null);

export function DocumentProvider({ children }: { children: React.ReactNode }) {
  const [document, setDocument] = useState<DocumentInfo | null>(null);
  return (
    <DocumentContext.Provider value={{ document, setDocument }}>
      {children}
    </DocumentContext.Provider>
  );
}

export function useDocument() {
  const ctx = useContext(DocumentContext);
  if (!ctx) throw new Error("useDocument must be used within DocumentProvider");
  return ctx;
}
