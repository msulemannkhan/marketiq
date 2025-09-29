import Image from "next/image";
import { Shield, Laptop, Brain } from "lucide-react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { AuthBranding } from "./AuthBranding";

export function AuthHero() {
  return (
    <div className="relative bg-slate-900">
      <div className="absolute inset-0 bg-black/50 z-10" />
      <Image
        src={BRAND_CONFIG.assets.authHeroImage}
        alt={BRAND_CONFIG.assets.authHeroAlt}
        fill
        className="object-cover blur-sm"
        priority
      />

      <div className="relative z-20 flex flex-col justify-between h-full p-12 text-white">
        {/* Brand Header - Top Left */}
        <AuthBranding variant="hero" />

        {/* Main Content - No Box */}
        <div className="w-full max-w-none">
          <h2 className="text-6xl font-bold mb-8 text-white leading-tight drop-shadow-2xl">
            {BRAND_CONFIG.hero.title}
          </h2>
          <p className="text-xl text-white/95 leading-relaxed mb-12 font-light max-w-2xl drop-shadow-lg">
            {BRAND_CONFIG.hero.subtitle}
          </p>

          {/* Features */}
          <div className="space-y-8">
            {BRAND_CONFIG.hero.features.map((feature, index) => {
              const IconComponent = feature.icon === 'Shield' ? Shield : feature.icon === 'Laptop' ? Laptop : Brain;
              const iconColors = {
                green: 'text-emerald-300',
                blue: 'text-sky-300',
                purple: 'text-violet-300'
              };

              return (
                <div key={index} className="flex items-center gap-5 group hover:translate-x-2 transition-all duration-300">
                  <div className="flex-shrink-0 p-4 bg-white/15 backdrop-blur-sm rounded-2xl border border-white/25 group-hover:bg-white/25 transition-all duration-300">
                    <IconComponent className={`h-6 w-6 ${iconColors[feature.color as keyof typeof iconColors]}`} />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-white font-semibold text-lg drop-shadow-md">{feature.text}</span>
                    <span className="text-white/70 text-sm font-light drop-shadow-sm">
                      {BRAND_CONFIG.auth.featureDescriptions[feature.color as keyof typeof BRAND_CONFIG.auth.featureDescriptions]}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="text-left">
          <p className="text-white/60 text-sm font-light">
            {BRAND_CONFIG.footer.copyright}
          </p>
        </div>
      </div>
    </div>
  );
}