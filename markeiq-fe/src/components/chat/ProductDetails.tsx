"use client";

import { Product } from '@/types/product';
import { Star, DollarSign, Package, HardDrive, Monitor, Cpu, Weight, Battery } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import Image from 'next/image';
import { useRouter } from 'next/navigation';

interface ProductDetailsProps {
  products: Product[];
  className?: string;
}

export function ProductDetails({ products, className }: ProductDetailsProps) {
  const router = useRouter();
  
  if (!products || products.length === 0) return null;
  return (
    <div className={cn("space-y-4", className)}>
      <h4 className="text-sm font-semibold text-foreground mb-3">
        Mentioned Products
      </h4>
      <div className="grid gap-4">
        {products.map((product) => (
          <div
            key={product.id}
            className="border rounded-xl p-4 bg-card hover:bg-accent/50 transition-colors"
          >
            <div className="flex gap-4">
              {/* Product Image */}
              <div className="flex-shrink-0">
                <div className="w-32 h-32 bg-muted rounded-lg flex items-center justify-center">
                  {product.image_url ? (
                    <Image
                      src={product.image_url}
                      alt={product.name}
                      width={128}
                      height={128}
                      className="w-full h-full object-cover rounded-lg"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        target.nextElementSibling?.classList.remove('hidden');
                      }}
                    />
                  ) : null}
                  <div className={cn(
                    "w-16 h-16 bg-gradient-to-br from-gray-600 to-gray-800 rounded-lg flex items-center justify-center text-white text-lg font-bold",
                    product.image_url ? "hidden" : ""
                  )}>
                    {product.brand.charAt(0)}
                  </div>
                </div>
              </div>

              {/* Product Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h5 className="font-semibold text-foreground text-sm leading-tight">
                      {product.name}
                    </h5>
                    <p className="text-muted-foreground text-xs">
                      {product.brand} {product.model}
                    </p>
                  </div>
                  <div className="text-right ml-4">
                    <div className="flex items-center gap-1 text-sm font-semibold text-foreground">
                      <DollarSign className="h-3 w-3" />
                      {product.base_price.toLocaleString()}
                    </div>
                    {product.original_price !== undefined && product.original_price > product.base_price && (
                      <div className="text-xs text-muted-foreground line-through">
                        ${product.original_price.toLocaleString()}
                      </div>
                    )}
                  </div>
                </div>

                {/* Ratings */}
                <div className="flex items-center gap-2 mb-3">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={cn(
                          "h-3 w-3",
                          i < Math.floor(product.rating)
                            ? "text-yellow-400 fill-yellow-400"
                            : "text-gray-300 dark:text-gray-600"
                        )}
                      />
                    ))}
                    <span className="text-xs text-muted-foreground ml-1">
                      {product.rating.toFixed(1)} ({product.review_count})
                    </span>
                  </div>
                  <div className="text-xs px-2 py-1 bg-muted rounded-md">
                    {product.availability.replace('_', ' ').toUpperCase()}
                  </div>
                </div>

                {/* Key Specifications */}
                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  {product.specs.processor && (
                    <div className="flex items-center gap-1">
                      <Cpu className="h-3 w-3" />
                      <span className="truncate">{product.specs.processor}</span>
                    </div>
                  )}
                  {product.specs.memory && (
                    <div className="flex items-center gap-1">
                      <Package className="h-3 w-3" />
                      <span>{product.specs.memory}</span>
                    </div>
                  )}
                  {product.specs.storage && (
                    <div className="flex items-center gap-1">
                      <HardDrive className="h-3 w-3" />
                      <span className="truncate">{product.specs.storage}</span>
                    </div>
                  )}
                  {product.specs.display_size && (
                    <div className="flex items-center gap-1">
                      <Monitor className="h-3 w-3" />
                      <span>{product.specs.display_size}</span>
                    </div>
                  )}
                  {product.specs.weight && (
                    <div className="flex items-center gap-1">
                      <Weight className="h-3 w-3" />
                      <span className="truncate">{product.specs.weight}</span>
                    </div>
                  )}
                  {product.specs.battery && (
                    <div className="flex items-center gap-1">
                      <Battery className="h-3 w-3" />
                      <span className="truncate">{product.specs.battery}</span>
                    </div>
                  )}
                </div>

                {/* Description */}
                {product.description && (
                  <p className="text-xs text-muted-foreground mt-2 line-clamp-2">
                    {product.description}
                  </p>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 mt-4">
              <Button size="sm" onClick={() => router.push(`/dashboard/catalog/${product.id}`)} variant="outline" className="text-xs h-8">
                View Details
              </Button>
              <Button size="sm" onClick={() => router.push(`/dashboard/catalog/${product.id}`)} variant="outline" className="text-xs h-8">
                Compare
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
