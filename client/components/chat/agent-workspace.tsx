"use client";

import { useMemo, useRef, useState } from "react";
import { toast } from "sonner";
import {
    BarChart3,
    BrainCircuit,
    FileText,
    Loader2,
    NotebookText,
    Search,
    ShieldCheck,
    Sparkles,
} from "lucide-react";
import { agentService } from "@/services/api";
import { useDocument } from "@/providers/document-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import type { AgentRequest, AgentResponse, AgentType } from "@/types";

const AGENT_META: Record<
    AgentType,
    {
        label: string;
        icon: typeof Search;
        description: string;
        defaults: string[];
        accent: string;
        modeLabel: string;
    }
> = {
    research: {
        label: "Research Agent",
        icon: Search,
        description: "Find answers and evidence from your documents.",
        defaults: [
            "What are the document's biggest challenges?",
            "What does the document say about risk and mitigation?",
        ],
        accent: "from-violet-500/20 to-indigo-500/10",
        modeLabel: "Evidence-led answer",
    },
    summary: {
        label: "Summary Agent",
        icon: NotebookText,
        description: "Generate concise business summaries and key takeaways.",
        defaults: [
            "Create an executive summary of this document.",
            "Summarize the document into key points and action items.",
        ],
        accent: "from-emerald-500/20 to-teal-500/10",
        modeLabel: "Business summary",
    },
    analyst: {
        label: "Analyst Agent",
        icon: BarChart3,
        description: "Analyze trends, comparisons, and document insights.",
        defaults: [
            "What are the major trends discussed in this report?",
            "Compare the key themes and highlight their implications.",
        ],
        accent: "from-sky-500/20 to-cyan-500/10",
        modeLabel: "Trend analysis",
    },
    document: {
        label: "Document Agent",
        icon: FileText,
        description: "Extract structured information, topics, and important document details.",
        defaults: [
            "Extract key topics and dates from the document.",
            "Generate a concise FAQ based on the document's contents.",
        ],
        accent: "from-amber-500/20 to-orange-500/10",
        modeLabel: "Document intelligence",
    },
    verification: {
        label: "Verification Agent",
        icon: ShieldCheck,
        description: "Check whether claims are actually supported by the document evidence.",
        defaults: [
            "Verify whether this answer is supported by the document evidence.",
            "Check the claims in this summary against the document.",
        ],
        accent: "from-rose-500/20 to-pink-500/10",
        modeLabel: "Evidence verification",
    },
};

export function AgentWorkspace() {
    const { document } = useDocument();
    const resultRef = useRef<HTMLDivElement | null>(null);
    const [selectedAgent, setSelectedAgent] = useState<AgentType>("research");
    const [agentInput, setAgentInput] = useState(AGENT_META.research.defaults[0]);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<AgentResponse | null>(null);

    const selectedMeta = useMemo(() => AGENT_META[selectedAgent], [selectedAgent]);

    const handleAgentSelect = (agent: AgentType) => {
        setSelectedAgent(agent);
        setResult(null);
        setAgentInput(AGENT_META[agent].defaults[0]);
    };

    const handleRun = async () => {
        if (!document) {
            toast.error("Select a document before running an agent.");
            return;
        }

        const question = agentInput.trim();
        if (!question) {
            toast.error("Please enter a task for the selected agent.");
            return;
        }

        const mode =
            selectedAgent === "summary"
                ? "executive"
                : selectedAgent === "analyst"
                    ? "analysis"
                    : selectedAgent === "document"
                        ? "extract"
                        : undefined;

        const request: AgentRequest = {
            agent: selectedAgent,
            document_id: document.id,
            question,
            mode,
        };

        setIsLoading(true);
        setResult(null);

        try {
            const response = await agentService.run(request);
            setResult(response);
            requestAnimationFrame(() => {
                resultRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
            });
        } catch (error) {
            toast.error(error instanceof Error ? error.message : "The agent could not complete the request.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="border-b border-border/60 bg-card/60 p-4 backdrop-blur-sm">
            <div className="mb-4 flex items-center justify-between gap-3">
                <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <BrainCircuit className="h-4 w-4" />
                    </div>
                    <div>
                        <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                            AI Document Workspace
                        </p>
                        <h2 className="text-base font-semibold">Multi-Agent Intelligence</h2>
                    </div>
                </div>
                {document && (
                    <div className="rounded-full border border-border bg-background px-2.5 py-1 text-[11px] text-muted-foreground">
                        {document.name}
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-5">
                {(Object.keys(AGENT_META) as AgentType[]).map((agent) => {
                    const meta = AGENT_META[agent];
                    const Icon = meta.icon;
                    const isActive = selectedAgent === agent;

                    return (
                        <button
                            key={agent}
                            type="button"
                            onClick={() => handleAgentSelect(agent)}
                            className={`rounded-xl border p-3 text-left transition-all ${isActive
                                    ? "border-primary/40 bg-primary/5 shadow-sm"
                                    : "border-border bg-background hover:border-primary/20 hover:bg-muted/40"
                                }`}
                        >
                            <div className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                                <Icon className="h-4 w-4" />
                            </div>
                            <p className="text-sm font-medium">{meta.label}</p>
                            <p className="mt-1 text-[11px] text-muted-foreground">{meta.description}</p>
                        </button>
                    );
                })}
            </div>

            <Card className="mt-4 overflow-hidden border-border/60">
                <div className={`border-b border-border/60 bg-gradient-to-r ${selectedMeta.accent} p-4`}>
                    <div className="flex items-center justify-between gap-4">
                        <CardTitle className="flex items-center gap-2 text-base">
                            <Sparkles className="h-4 w-4 text-primary" />
                            {selectedMeta.label}
                        </CardTitle>
                        <span className="rounded-full border border-border bg-background/70 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.14em] text-muted-foreground">
                            {selectedMeta.modeLabel}
                        </span>
                    </div>
                </div>

                <CardContent className="space-y-4 p-4">
                    <Textarea
                        value={agentInput}
                        onChange={(event) => setAgentInput(event.target.value)}
                        placeholder={
                            document
                                ? `${selectedMeta.label} prompt...`
                                : "Select a document to begin."
                        }
                        disabled={!document || isLoading}
                        className="min-h-[90px] text-sm"
                    />

                    <div className="flex flex-wrap gap-2">
                        {selectedMeta.defaults.map((example) => (
                            <button
                                key={example}
                                type="button"
                                onClick={() => setAgentInput(example)}
                                className="rounded-full border border-border bg-background px-2.5 py-1 text-[11px] text-muted-foreground transition-colors hover:border-primary/30 hover:text-foreground"
                            >
                                {example}
                            </button>
                        ))}
                    </div>

                    <div className="flex items-center justify-between gap-3">
                        <p className="text-[11px] text-muted-foreground">
                            {document ? `Working on ${document.name}` : "No document selected"}
                        </p>
                        <Button onClick={handleRun} disabled={!document || isLoading} className="w-full sm:w-auto">
                            {isLoading ? (
                                <>
                                    <Loader2 className="h-4 w-4 animate-spin" /> Running agent...
                                </>
                            ) : (
                                `Run ${selectedMeta.label}`
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {result && (
                <div ref={resultRef} className="mt-4 rounded-xl border border-border bg-background p-4">
                    <div className="mb-2 flex items-center justify-between gap-4">
                        <p className="text-sm font-semibold">Agent Result</p>
                        {result.verification && (
                            <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-1 text-[10px] font-medium uppercase tracking-[0.12em] text-emerald-600">
                                {result.verification.verified ? "Verified" : "Needs Evidence"}
                            </span>
                        )}
                    </div>

                    <div className="space-y-4 text-sm text-foreground">
                        <div className="rounded-lg bg-muted/50 p-3">
                            <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                Answer
                            </p>
                            <p className="whitespace-pre-wrap leading-relaxed">{result.answer}</p>
                        </div>

                        {result.summary && (
                            <div className="rounded-lg bg-muted/50 p-3">
                                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                    Summary
                                </p>
                                <p className="whitespace-pre-wrap leading-relaxed">{result.summary}</p>
                            </div>
                        )}

                        {result.activity?.length ? (
                            <div className="rounded-lg bg-muted/50 p-3">
                                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                    Agent Activity
                                </p>
                                <ul className="space-y-2">
                                    {result.activity.map((step) => (
                                        <li key={step} className="flex items-center gap-2 text-sm">
                                            <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500" />
                                            <span>{step}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ) : null}

                        {result.findings?.length ? (
                            <div className="rounded-lg bg-muted/50 p-3">
                                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                    Findings
                                </p>
                                <ul className="list-disc space-y-1 pl-5">
                                    {result.findings.map((finding) => (
                                        <li key={finding}>{finding}</li>
                                    ))}
                                </ul>
                            </div>
                        ) : null}

                        {result.sources?.length ? (
                            <div className="rounded-lg bg-muted/50 p-3">
                                <p className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-muted-foreground">
                                    Sources
                                </p>
                                <ul className="space-y-2">
                                    {result.sources.map((source) => (
                                        <li
                                            key={`${source.chunk_id}-${source.heading}`}
                                            className="rounded border border-border bg-background px-2 py-1.5 text-xs"
                                        >
                                            <span className="font-medium">{source.heading || "Document section"}</span>
                                            <span className="ml-2 text-muted-foreground">similarity {source.similarity}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ) : null}

                        {result.verification && (
                            <div className="rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-3 text-xs text-emerald-700 dark:text-emerald-300">
                                <p className="font-semibold uppercase tracking-[0.14em]">Verification</p>
                                <p className="mt-1">Confidence: {result.verification.confidence}</p>
                                {result.verification.supported_claims.length > 0 && (
                                    <p className="mt-1">Supported: {result.verification.supported_claims.join("; ")}</p>
                                )}
                                {result.verification.unsupported_claims.length > 0 && (
                                    <p className="mt-1">Unsupported: {result.verification.unsupported_claims.join("; ")}</p>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
