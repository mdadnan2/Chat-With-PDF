import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "sonner";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { DocumentProvider } from "@/providers/document-provider";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PDFChat — Chat With Your Documents",
  description: "Upload any PDF and get instant AI-powered answers using RAG technology.",
  keywords: ["PDF", "AI", "chat", "RAG", "document", "Gemini"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ThemeProvider>
          <QueryProvider>
            <DocumentProvider>
              {children}
              <Toaster position="top-right" richColors closeButton />
            </DocumentProvider>
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
