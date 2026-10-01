"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-16 sm:py-20">
      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-2xl bg-primary p-7 text-center sm:p-10"
        >
          <div className="relative z-10">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white">
              <Sparkles className="h-3 w-3" />
              Upload a PDF and start a conversation
            </div>

            <h2 className="text-2xl font-semibold text-white sm:text-3xl">
              Ready to chat with your PDF?
            </h2>
            <p className="mt-4 text-base text-white/80 max-w-md mx-auto">
              Upload your document and get answers grounded in its contents.
            </p>

            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              {/* Dark button — always readable on the purple gradient */}
              <Link
                href="/upload"
                className="inline-flex min-h-11 items-center gap-2 rounded-lg bg-white px-6 py-2.5 text-sm font-semibold transition-colors hover:bg-white/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-primary"
                style={{ color: "#4f46e5" }}
              >
                Upload a PDF <ArrowRight className="h-4 w-4" style={{ color: "#4f46e5" }} />
              </Link>
              <Link
                href="/#features"
                className="inline-flex items-center gap-2 rounded-xl border-2 border-white/40 px-8 py-3 text-sm font-semibold text-white hover:bg-white/15 transition-all duration-200"
              >
                Learn more
              </Link>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
