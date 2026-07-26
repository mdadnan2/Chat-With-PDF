"use client";

import { motion } from "framer-motion";
import { Zap, Shield, Brain, MessageSquare, FileSearch, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Brain,
    title: "RAG-Powered Intelligence",
    description: "Retrieval-Augmented Generation ensures answers are grounded in your document's actual content.",
    color: "text-violet-500",
    bg: "bg-violet-500/10",
  },
  {
    icon: Zap,
    title: "Instant Answers",
    description: "Get precise answers in seconds. No more scrolling through hundreds of pages manually.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  {
    icon: MessageSquare,
    title: "Natural Conversation",
    description: "Ask follow-up questions naturally. The AI maintains context throughout your conversation.",
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    icon: FileSearch,
    title: "Deep Document Analysis",
    description: "Semantic search across your entire document finds relevant information even with different wording.",
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Shield,
    title: "Accurate & Reliable",
    description: "Answers are sourced directly from your document, minimizing hallucinations.",
    color: "text-rose-500",
    bg: "bg-rose-500/10",
  },
  {
    icon: Sparkles,
    title: "Gemini AI Backend",
    description: "Powered by Google's Gemini model for state-of-the-art language understanding.",
    color: "text-primary",
    bg: "bg-primary/10",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-sm font-medium text-primary mb-3"
          >
            Everything you need
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            Powerful features, simple experience
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-4 text-muted-foreground max-w-xl mx-auto"
          >
            Everything you need to extract insights from your documents instantly.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              <Card className="group h-full hover:shadow-md hover:border-primary/20 transition-all duration-300">
                <CardContent className="p-6">
                  <div className={`mb-4 inline-flex h-10 w-10 items-center justify-center rounded-xl ${feature.bg}`}>
                    <feature.icon className={`h-5 w-5 ${feature.color}`} />
                  </div>
                  <h3 className="font-semibold text-foreground mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
