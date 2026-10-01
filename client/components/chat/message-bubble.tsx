"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Copy, Check, User, Sparkles, ShieldCheck, ShieldAlert, ShieldX, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { MarkdownContent } from "@/components/chat/markdown-content";
import type { Message } from "@/types";

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);
  const reduceMotion = useReducedMotion();
  const isUser = message.role === "user";
  const verificationStatus = message.verification?.status ?? (
    message.verification?.verified ? "SUPPORTED" : "INSUFFICIENT_EVIDENCE"
  );
  const agentLabel = message.agent
    ? `${message.agent.charAt(0).toUpperCase()}${message.agent.slice(1)}`
    : null;

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={reduceMotion ? false : { opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.18 }}
      className={cn("group flex w-full items-start gap-3", isUser && "justify-end")}
    >
      {!isUser && (
        <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary">
          <Sparkles className="h-3.5 w-3.5" />
        </div>
      )}

      <div className={cn("min-w-0 max-w-[min(100%,48rem)]", isUser && "max-w-[85%]")}>
        {isUser ? (
          <div className="rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm leading-relaxed text-primary-foreground">
            <p className="whitespace-pre-wrap">{message.content}</p>
          </div>
        ) : (
          <div className="min-w-0 text-sm leading-relaxed text-foreground">
            <MarkdownContent content={message.content} className="min-w-0" />

            {(message.agent || message.routing || message.verification) && (
              <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-2">
                {agentLabel && (
                  <details className="group/routing text-xs text-muted-foreground">
                    <summary className="flex w-fit cursor-pointer list-none items-center gap-1.5 rounded-full border border-border px-2.5 py-1 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                      Handled by {agentLabel}
                      <ChevronDown className="h-3 w-3 transition-transform group-open/routing:rotate-180" />
                    </summary>
                    {message.routing?.reason && (
                      <p className="disclosure-panel mt-2 max-w-sm rounded-md bg-muted px-3 py-2 text-xs leading-relaxed">
                        {message.routing.reason}
                      </p>
                    )}
                  </details>
                )}
                {message.verification && (
                  <details className="group/verification text-xs">
                    <summary className={cn(
                      "flex cursor-pointer list-none items-center gap-1.5 rounded-full border px-2.5 py-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                      verificationStatus === "SUPPORTED" && "border-emerald-500/30 text-emerald-700 dark:text-emerald-300",
                      verificationStatus === "UNSUPPORTED" && "border-destructive/30 text-destructive",
                      verificationStatus === "INSUFFICIENT_EVIDENCE" && "border-amber-500/30 text-amber-700 dark:text-amber-300",
                    )}>
                      {verificationStatus === "SUPPORTED" ? <ShieldCheck className="h-3.5 w-3.5" /> : null}
                      {verificationStatus === "UNSUPPORTED" ? <ShieldX className="h-3.5 w-3.5" /> : null}
                      {verificationStatus === "INSUFFICIENT_EVIDENCE" ? <ShieldAlert className="h-3.5 w-3.5" /> : null}
                      {verificationStatus === "SUPPORTED" ? "Supported" : verificationStatus === "UNSUPPORTED" ? "Unsupported" : "Insufficient evidence"}
                      <ChevronDown className="h-3 w-3 transition-transform group-open/verification:rotate-180" />
                    </summary>
                    {(message.verification.explanation || message.verification.supported_claims.length > 0 || message.verification.unsupported_claims.length > 0 || message.verification.missing_evidence.length > 0) && (
                      <div className="disclosure-panel mt-2 max-w-2xl rounded-md bg-muted px-3 py-2 text-xs">
                        {message.verification.explanation && <MarkdownContent content={message.verification.explanation} />}
                        {message.verification.supported_claims.length > 0 && (
                          <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                            {message.verification.supported_claims.map((claim) => <li key={claim}>Supported: {claim}</li>)}
                          </ul>
                        )}
                        {message.verification.unsupported_claims.length > 0 && (
                          <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                            {message.verification.unsupported_claims.map((claim) => <li key={claim}>Unsupported: {claim}</li>)}
                          </ul>
                        )}
                        {message.verification.missing_evidence.length > 0 && (
                          <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                            {message.verification.missing_evidence.map((claim) => <li key={claim}>Missing evidence: {claim}</li>)}
                          </ul>
                        )}
                      </div>
                    )}
                  </details>
                )}
              </div>
            )}

            {message.summary && message.summary.trim() !== message.content.trim() && (
              <details className="group mt-3 max-w-2xl text-xs text-muted-foreground">
                <summary className="flex w-fit cursor-pointer list-none items-center gap-1.5 rounded-full border border-border px-2.5 py-1 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  Summary
                  <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" />
                </summary>
                <div className="disclosure-panel mt-2 text-sm text-foreground">
                  <MarkdownContent content={message.summary} />
                </div>
              </details>
            )}

            {message.findings?.length ? (
              <details className="group mt-3 max-w-2xl text-xs text-muted-foreground">
                <summary className="flex w-fit cursor-pointer list-none items-center gap-1.5 rounded-full border border-border px-2.5 py-1 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  Findings · {message.findings.length}
                  <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" />
                </summary>
                <ul className="disclosure-panel mt-2 list-disc space-y-1 pl-5 text-sm text-foreground">
                  {message.findings.map((finding) => <li key={finding}>{finding}</li>)}
                </ul>
              </details>
            ) : null}

            {message.activity?.length ? (
              <details className="group mt-2 max-w-2xl text-[11px] text-muted-foreground">
                <summary className="flex w-fit cursor-pointer list-none items-center gap-1 hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  Processing details <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" />
                </summary>
                <ul className="disclosure-panel mt-1 list-disc space-y-0.5 pl-5">
                  {message.activity.map((step) => <li key={step}>{step}</li>)}
                </ul>
              </details>
            ) : null}

            {message.sources?.length ? (
              <details className="group mt-3 max-w-2xl text-xs text-muted-foreground">
                <summary className="flex w-fit cursor-pointer list-none items-center gap-1.5 rounded-full border border-border px-2.5 py-1 hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                  Sources · {message.sources.length}
                  <ChevronDown className="h-3 w-3 transition-transform group-open:rotate-180" />
                </summary>
                <ul className="disclosure-panel mt-2 space-y-1.5">
                  {message.sources.map((source) => (
                    <li key={`${source.chunk_id}-${source.heading}`} className="break-words text-xs">
                      {source.heading || "Document section"}
                    </li>
                  ))}
                </ul>
              </details>
            ) : null}
          </div>
        )}

        <div className={cn("mt-1 flex items-center gap-2 px-1", isUser && "justify-end")}>
          <span className="text-[10px] text-muted-foreground">
            {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </span>
          {!isUser && (
            <button
              onClick={copyToClipboard}
              className="text-muted-foreground opacity-0 transition-opacity hover:text-foreground focus-visible:opacity-100 group-hover:opacity-100"
              aria-label="Copy message"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
            </button>
          )}
        </div>
      </div>
      {isUser && (
        <div className="mt-1 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-muted text-muted-foreground">
          <User className="h-3.5 w-3.5" />
        </div>
      )}
    </motion.div>
  );
}
