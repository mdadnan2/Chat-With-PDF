"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Sparkles } from "lucide-react";

export function CTASection() {
  return (
    <section className="py-24 sm:py-32">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl p-12 text-center"
          style={{
            background: "linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #6d28d9 100%)",
          }}
        >
          {/* Subtle dark overlay for contrast */}
          <div className="absolute inset-0 bg-black/20 rounded-3xl" />

          {/* Decorative blobs — toned down */}
          <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-3xl">
            <div className="absolute -top-16 -right-16 h-48 w-48 rounded-full bg-white/8 blur-2xl" />
            <div className="absolute -bottom-16 -left-16 h-48 w-48 rounded-full bg-white/8 blur-2xl" />
          </div>

          <div className="relative z-10">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-medium text-white">
              <Sparkles className="h-3 w-3" />
              Free to use · No signup required
            </div>

            <h2 className="text-3xl font-bold text-white sm:text-4xl drop-shadow-sm">
              Ready to chat with your PDF?
            </h2>
            <p className="mt-4 text-base text-white/80 max-w-md mx-auto">
              Upload your document and start getting answers in seconds.
            </p>

            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              {/* Dark button — always readable on the purple gradient */}
              <Link
                href="/upload"
                className="inline-flex items-center gap-2 rounded-xl bg-white/95 px-8 py-3 text-sm font-bold shadow-xl hover:bg-white transition-all duration-200 active:scale-[0.98]"
                style={{ color: "#4f46e5" }}
              >
                Get Started Free <ArrowRight className="h-4 w-4" style={{ color: "#4f46e5" }} />
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
