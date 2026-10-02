"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";

const delays = [0, 0.12, 0.22, 0.32, 0.44];

export function HeroSection() {
  return (
    <section className="relative overflow-hidden py-12 sm:py-16 lg:py-20">
      {/* A restrained accent behind the hero content */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-0 h-80 w-[min(90vw,44rem)] -translate-x-1/2 rounded-full bg-primary/8 blur-[100px]" />
      </div>

      <div className="mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delays[0], duration: 0.5 }}
          className="mb-8 inline-flex items-center gap-2 rounded-full border border-primary/25 bg-primary/8 px-4 py-1.5 text-sm font-medium text-primary"
        >
          <Sparkles className="h-3.5 w-3.5" />
          AI-powered multi-agent document assistant
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delays[1], duration: 0.5 }}
          className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl"
        >
          Chat With Your{" "}
          <span className="relative bg-gradient-to-r from-primary via-violet-400 to-indigo-400 bg-clip-text text-transparent">
            PDF
          </span>
        </motion.h1>

        {/* Subheading */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delays[2], duration: 0.5 }}
          className="mx-auto mt-5 max-w-xl text-lg text-muted-foreground leading-relaxed"
        >
          Upload a PDF and ask questions in plain language. Get answers grounded in your document, with automatic specialist selection, source references, and claim verification.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delays[3], duration: 0.5 }}
          className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center"
        >
          <Button asChild size="lg" className="gap-2 px-8 shadow-lg shadow-primary/25">
            <Link href="/upload">
              Upload PDF <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="gap-2">
            <Link href="/#how-it-works">See How It Works</Link>
          </Button>
        </motion.div>

        {/* App mockup */}
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: delays[4], duration: 0.6 }}
          className="mt-10 mx-auto max-w-3xl"
        >
          <div className="relative overflow-hidden rounded-2xl border border-border bg-card shadow-lg shadow-black/10">
            {/* Window chrome */}
            <div className="flex items-center gap-1.5 border-b border-border bg-muted/40 px-4 py-3">
              <div className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-yellow-500/80" />
              <div className="h-2.5 w-2.5 rounded-full bg-green-500/80" />
              <div className="mx-auto flex items-center gap-1.5 rounded-md border border-border/60 bg-background/60 px-3 py-1">
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
                <span className="text-[11px] text-muted-foreground">Chat with PDF</span>
              </div>
            </div>

            <div className="grid min-h-[260px] grid-cols-5">
              {/* Sidebar */}
              <div className="col-span-2 hidden border-r border-border bg-muted/20 p-4 sm:block sm:space-y-4">
                {/* Doc card */}
                <div className="rounded-xl border border-primary/20 bg-primary/5 p-3 space-y-3">
                  <div className="flex items-center gap-2.5">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/20">
                      <FileText className="h-4 w-4 text-primary" />
                    </div>
                    <div className="space-y-1.5 flex-1">
                      <div className="h-2 w-28 rounded-full bg-foreground/20" />
                      <div className="h-1.5 w-16 rounded-full bg-muted-foreground/25" />
                    </div>
                  </div>
                  <div className="space-y-1.5">
                    {["PDF selected", "Ready to chat"].map((item) => (
                      <div key={item} className="flex items-center gap-2">
                        <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shrink-0" />
                        <span className="text-[11px] text-muted-foreground">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
                {/* Skeleton lines */}
                <div className="space-y-2 pt-1">
                  <div className="h-1.5 w-full rounded-full bg-border/60" />
                  <div className="h-1.5 w-4/5 rounded-full bg-border/40" />
                  <div className="h-1.5 w-3/5 rounded-full bg-border/30" />
                </div>
              </div>

              {/* Chat area */}
              <div className="col-span-5 flex flex-col gap-3 p-4 sm:col-span-3">
                {/* User message */}
                <div className="flex justify-end">
                  <div className="rounded-2xl rounded-tr-sm bg-primary px-3 py-2 text-[11px] text-primary-foreground max-w-[75%] leading-relaxed">
                    What are the key findings?
                  </div>
                </div>
                {/* AI message */}
                <div className="flex gap-2 items-start">
                  <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center shrink-0 mt-0.5">
                    <Sparkles className="h-2.5 w-2.5 text-primary" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm bg-muted px-3 py-2 text-[11px] text-muted-foreground max-w-[85%] leading-relaxed">
                    The document highlights three key findings. Review the relevant sections or ask a follow-up question.
                  </div>
                </div>
                {/* Second user message */}
                <div className="flex justify-end">
                  <div className="rounded-2xl rounded-tr-sm bg-primary/80 px-3 py-2 text-[11px] text-primary-foreground max-w-[65%] leading-relaxed">
                    Tell me more about the cost reduction
                  </div>
                </div>
                {/* Typing indicator */}
                <div className="flex gap-2 items-center">
                  <div className="h-5 w-5 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                    <Sparkles className="h-2.5 w-2.5 text-primary" />
                  </div>
                  <div className="rounded-2xl rounded-tl-sm bg-muted px-3 py-2.5 flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <div key={i} className="h-1.5 w-1.5 rounded-full bg-muted-foreground/50 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                </div>
                {/* Input bar */}
                <div className="mt-auto flex items-center gap-2 rounded-xl border border-border bg-background/80 px-3 py-2">
                  <span className="text-[11px] text-muted-foreground flex-1">Ask a question...</span>
                  <div className="h-6 w-6 rounded-lg bg-primary flex items-center justify-center">
                    <ArrowRight className="h-3 w-3 text-primary-foreground" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
