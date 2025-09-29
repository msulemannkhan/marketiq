"use client";

import { Product } from "@/types/product";
import { ProductCard } from "./ProductCard";

interface ProductGridProps {
  products: Product[];
  viewMode: 'grid' | 'list';
  loading?: boolean;
}

export function ProductGrid({ products, viewMode, loading }: ProductGridProps) {
  // Show skeleton loading states
  if (loading) {
    return (
      <div className={`grid gap-6 ${
        viewMode === 'grid'
          ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
          : 'grid-cols-1'
      }`}>
        {[...Array(12)].map((_, i) => (
          <div
            key={i}
            className={`animate-pulse bg-card border border-border rounded-2xl overflow-hidden ${
              viewMode === 'grid' ? 'h-96' : 'h-32'
            }`}
          >
            {viewMode === 'grid' ? (
              <>
                {/* Image skeleton */}
                <div className="aspect-[4/3] bg-[#232323]" />
                {/* Content skeleton */}
                <div className="p-6 space-y-3">
                  <div className="h-4 bg-[#232323] rounded w-3/4" />
                  <div className="h-3 bg-[#232323] rounded w-1/2" />
                  <div className="space-y-2">
                    <div className="h-3 bg-[#232323] rounded w-full" />
                    <div className="h-3 bg-[#232323] rounded w-5/6" />
                    <div className="h-3 bg-[#232323] rounded w-4/5" />
                  </div>
                  <div className="h-6 bg-[#232323] rounded w-1/3" />
                  <div className="h-10 bg-[#232323] rounded" />
                </div>
              </>
            ) : (
              <div className="flex gap-6 p-6">
                {/* Image skeleton */}
                <div className="w-48 h-32 bg-[#232323] rounded-xl flex-shrink-0" />
                {/* Content skeleton */}
                <div className="flex-1 space-y-3">
                  <div className="h-5 bg-[#232323] rounded w-3/4" />
                  <div className="h-3 bg-[#232323] rounded w-1/3" />
                  <div className="space-y-2">
                    <div className="h-3 bg-[#232323] rounded w-full" />
                    <div className="h-3 bg-[#232323] rounded w-4/5" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="h-4 bg-[#232323] rounded w-1/4" />
                    <div className="h-6 bg-[#232323] rounded w-1/5" />
                  </div>
                  <div className="flex gap-3">
                    <div className="h-10 bg-[#232323] rounded flex-1" />
                    <div className="h-10 bg-[#232323] rounded w-20" />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  }

  // Show empty state if no products
  if (!products || products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="text-muted-foreground">No products found</div>
      </div>
    );
  }

  // Render products
  return (
    <div className={`grid gap-6 ${
      viewMode === 'grid'
        ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4'
        : 'grid-cols-1'
    }`}>
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          viewMode={viewMode}
        />
      ))}
    </div>
  );
}