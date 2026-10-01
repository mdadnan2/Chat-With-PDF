import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Toaster } from "sonner";
import { MotionConfig } from "framer-motion";
import { ThemeProvider } from "@/providers/theme-provider";
import { QueryProvider } from "@/providers/query-provider";
import { DocumentProvider } from "@/providers/document-provider";
import { AuthProvider } from "@/providers/auth-provider";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Chat with PDF — Chat with your documents",
  description: "Upload any PDF and get instant AI-powered answers using RAG technology.",
  keywords: ["PDF", "AI", "chat", "RAG", "document", "Gemini"],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <MotionConfig reducedMotion="user">
          <ThemeProvider>
            <QueryProvider>
              <AuthProvider>
                <DocumentProvider>
                  {children}
                  <Toaster position="top-right" richColors closeButton />
                </DocumentProvider>
              </AuthProvider>
            </QueryProvider>
          </ThemeProvider>
        </MotionConfig>
      </body>
    </html>
  );
}
