"use client";

import { motion } from "framer-motion";
import { Zap, Shield, MessageSquare, FileSearch } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Zap,
    title: "Grounded answers",
    description: "Get clear responses based on the content of your document.",
    color: "text-amber-500",
    bg: "bg-amber-500/10",
  },
  {
    icon: MessageSquare,
    title: "Natural conversation",
    description: "Ask follow-up questions in plain language as you explore a document.",
    color: "text-blue-500",
    bg: "bg-blue-500/10",
  },
  {
    icon: FileSearch,
    title: "Document analysis",
    description: "Find relevant details across your document, even when you phrase a question differently.",
    color: "text-emerald-500",
    bg: "bg-emerald-500/10",
  },
  {
    icon: Shield,
    title: "Sources and verification",
    description: "Review the document sections behind an answer and see when evidence is limited.",
    color: "text-rose-500",
    bg: "bg-rose-500/10",
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="py-16 sm:py-20">
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10 text-center sm:mb-12">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-sm font-medium text-primary mb-3"
          >
            Made for document questions
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            A simple way to explore your PDFs
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-4 text-muted-foreground max-w-xl mx-auto"
          >
            Ask, explore, and verify information in one focused chat.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.4 }}
            >
              <Card className="h-full border-border/80 shadow-none transition-colors duration-200 hover:border-primary/30">
                <CardContent className="p-5">
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
        <div className="mx-auto mt-12 max-w-3xl border-t border-border pt-8 text-center">
          <h3 className="text-base font-semibold">The right specialist, automatically</h3>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            Chat-With-PDF selects the best specialist for each question: Research, Summary, Analyst, Document, or Verification. You can simply ask; routing happens automatically.
          </p>
        </div>
      </div>
    </section>
  );
}
