"use client";

import { Recommendation } from "@/types/chat";
import { Star, DollarSign, Package, HardDrive, Monitor, Cpu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface RecommendationsProps {
  recommendations: Recommendation[];
  className?: string;
}

export function Recommendations({ recommendations, className }: RecommendationsProps) {
  const router = useRouter();
  
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className={cn("space-y-4", className)}>
      <h4 className="text-sm font-semibold text-foreground mb-3">
        Recommended Products
      </h4>
      <div className="grid gap-4">
        {recommendations.map((rec) => (
          <div
            key={rec.variant_id}
            className="border rounded-xl p-4 bg-card hover:bg-accent/50 transition-colors"
          >
            <div className="flex gap-4">
              {/* Product Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-semibold text-foreground text-sm leading-tight">
                      {rec.product_name}
                    </h5>
                    <p className="text-muted-foreground text-xs">
                      {rec.configuration.brand} • SKU: {rec.variant_id}
                    </p>
                  </div>
                  <div className="text-right ml-4">
                    <div className="flex items-center gap-1 text-sm font-semibold text-foreground">
                      <DollarSign className="h-3 w-3" />
                      ${rec.price.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      {Math.round(rec.score * 10)}/10
                    </div>
                  </div>
                </div>

                {/* Configuration */}
                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground mb-3">
                  <div className="flex items-center gap-1">
                    <Cpu className="h-3 w-3" />
                    <span className="truncate">{rec.configuration.processor}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Package className="h-3 w-3" />
                    <span>{rec.configuration.memory}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <HardDrive className="h-3 w-3" />
                    <span className="truncate">{rec.configuration.storage}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Monitor className="h-3 w-3" />
                    <span>{rec.configuration.display}</span>
                  </div>
                </div>

                {/* Rationale */}
                <p className="text-xs text-muted-foreground mb-3 p-2 bg-muted/50 rounded-md">
                  <strong>Why recommended:</strong> {rec.rationale}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 mt-4">
              <Button 
                size="sm" 
                onClick={() => router.push(`/dashboard/catalog/${rec.variant_id}`)} 
                variant="outline" 
                className="text-xs h-8"
              >
                View Details
              </Button>
              <Button 
                size="sm" 
                onClick={() => router.push(`/dashboard/catalog/${rec.variant_id}`)} 
                variant="outline" 
                className="text-xs h-8"
              >
                Compare
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
