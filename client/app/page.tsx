import { Navbar } from "@/components/layout/navbar";
import { HeroSection } from "@/components/layout/hero-section";
import { FeaturesSection } from "@/components/layout/features-section";
import { HowItWorksSection } from "@/components/layout/how-it-works-section";
import { CTASection } from "@/components/layout/cta-section";
import { Footer } from "@/components/layout/footer";

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <FeaturesSection />
        <HowItWorksSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
