import { Laptop } from "lucide-react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";

interface AuthBrandingProps {
  variant?: "mobile" | "hero";
  className?: string;
}

export function AuthBranding({ variant = "mobile", className = "" }: AuthBrandingProps) {
  if (variant === "hero") {
    return (
      <div className={`flex items-center gap-3 ${className}`}>
        <div className="p-2 bg-gradient-to-br from-white/15 to-white/10 backdrop-blur-md rounded-xl border border-white/20 shadow-lg">
          <Laptop className="h-6 w-6 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white drop-shadow-lg">
            {BRAND_CONFIG.name}
          </h1>
          <p className="text-sm text-white/90 font-medium drop-shadow-md">
            {BRAND_CONFIG.tagline}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`lg:hidden flex items-center justify-center gap-3 mb-8 ${className}`}>
      <div className="p-2 bg-primary/10 rounded-lg">
        <Laptop className="h-8 w-8 text-primary" />
      </div>
      <div>
        <h1 className="text-2xl font-bold text-foreground">{BRAND_CONFIG.name}</h1>
        <p className="text-sm text-muted-foreground">{BRAND_CONFIG.tagline}</p>
      </div>
    </div>
  );
}