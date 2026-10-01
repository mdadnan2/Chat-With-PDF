"use client";

import { motion } from "framer-motion";
import { Upload, Cpu, MessageSquare } from "lucide-react";

const steps = [
  {
    icon: Upload,
    step: "01",
    title: "Upload your PDF",
    description: "Drag and drop or click to upload any PDF document up to 50MB.",
  },
  {
    icon: Cpu,
    step: "02",
    title: "AI processes it",
    description: "We prepare the document so relevant details can support your answers.",
  },
  {
    icon: MessageSquare,
    step: "03",
    title: "Start chatting",
    description: "Ask questions naturally and get answers grounded in the document.",
  },
];

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="bg-muted/20 py-16 sm:py-20">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="mb-10 text-center sm:mb-12">
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-sm font-medium text-primary mb-3"
          >
            Simple process
          </motion.p>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl"
          >
            How it works
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="mt-4 text-muted-foreground"
          >
            Three simple steps to explore your document.
          </motion.p>
        </div>

        <div className="relative grid grid-cols-1 gap-12 md:grid-cols-3 md:gap-8">
          {/* Connector line — sits between icon centers */}
          <div className="absolute top-[28px] left-[calc(16.66%+28px)] right-[calc(16.66%+28px)] hidden h-px md:block">
            <div className="h-full w-full bg-border" />
          </div>

          {steps.map((step, i) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.15 }}
              className="flex flex-col items-center text-center"
            >
              {/* Icon circle */}
              <div className="relative mb-6 z-10">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl border-2 border-primary/30 bg-primary/10 shadow-lg shadow-primary/10">
                  <step.icon className="h-6 w-6 text-primary" />
                </div>
                {/* Step number badge */}
                <span className="absolute -top-2 -right-2 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[9px] font-bold text-primary-foreground shadow-md">
                  {i + 1}
                </span>
              </div>

              <h3 className="font-semibold text-foreground mb-2 text-base">{step.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed max-w-[220px]">
                {step.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
