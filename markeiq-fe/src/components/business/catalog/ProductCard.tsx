"use client";

import { Product } from "@/types/product";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Star, Heart, BarChart3, Cpu, HardDrive, Monitor } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

interface ProductCardProps {
  product: Product;
  viewMode: 'grid' | 'list';
}

export function ProductCard({ product, viewMode }: ProductCardProps) {
  const [imageError, setImageError] = useState(false);
  const [isWishlisted, setIsWishlisted] = useState(false);

  const discountPercentage = product.original_price
    ? Math.round(((product.original_price - product.base_price) / product.original_price) * 100)
    : null;

  // Get the first image from product_images array, fallback to image_url
  const getProductImage = () => {
    if (product.product_images && product.product_images.length > 0) {
      return product.product_images[0].url;
    }
    return product.image_url || BRAND_CONFIG.assets.productPlaceholder;
  };

  const getProductImageAlt = () => {
    if (product.product_images && product.product_images.length > 0) {
      return product.product_images[0].alt;
    }
    return product.name;
  };

  const getAvailabilityColor = (availability: string) => {
    switch (availability.toLowerCase()) {
      case 'available':
      case 'in stock': return 'bg-green-50 text-green-700 dark:bg-green-900 dark:text-green-300';
      case 'out of stock':
      case 'currently out of stock': return 'bg-red-50 text-red-700 dark:bg-red-900 dark:text-red-300';
      case 'pre order':
      case 'pre-order': return 'bg-blue-50 text-blue-700 dark:bg-blue-900 dark:text-blue-300';
      case 'limited stock':
      case 'hurry, last few remaining': return 'bg-orange-50 text-orange-700 dark:bg-orange-900 dark:text-orange-300';
      default: return 'bg-gray-50 text-gray-700 dark:bg-gray-900 dark:text-gray-300';
    }
  };

  const getAvailabilityText = (availability: string) => {
    switch (availability.toLowerCase()) {
      case 'available':
      case 'in stock': return BRAND_CONFIG.catalog.productCard.inStock;
      case 'out of stock':
      case 'currently out of stock': return BRAND_CONFIG.catalog.productCard.outOfStock;
      case 'pre order':
      case 'pre-order': return BRAND_CONFIG.catalog.productCard.preOrder;
      case 'limited stock':
      case 'hurry, last few remaining': return 'Limited Stock';
      default: return availability;
    }
  };

  if (viewMode === 'list') {
    return (
      <div className="bg-card border border-border rounded-2xl p-6 hover:shadow-lg transition-all duration-300 group">
        <div className="flex gap-6">
          {/* Product Image */}
          <div className="relative w-48 h-32 flex-shrink-0">
            <Image
              src={imageError ? BRAND_CONFIG.assets.productPlaceholder : getProductImage()}
              alt={getProductImageAlt()}
              fill
              className="object-cover rounded-xl"
              onError={() => setImageError(true)}
            />
            {discountPercentage && (
              <Badge className="absolute top-2 left-2 bg-red-500 text-white">
                -{discountPercentage}%
              </Badge>
            )}
          </div>

          {/* Product Info */}
          <div className="flex-1 space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors
                ">
                  <Link href={`/dashboard/catalog/${product.id}`} className="line-clamp-1">
                    {product.name}
                  </Link>
                </h3>
                <p className="text-muted-foreground text-sm">{product.brand}</p>
              </div>

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsWishlisted(!isWishlisted)}
                className="p-2"
              >
                <Heart className={`h-4 w-4 ${isWishlisted ? 'fill-red-500 text-red-500' : ''}`} />
              </Button>
            </div>

            {/* Specs */}
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Cpu className="h-4 w-4 flex-shrink-0" />
                <span className="line-clamp-1 text-red-400">{product.specs.processor_brand}</span>
              </span>
              <span className="flex items-center gap-1">
                <HardDrive className="h-4 w-4 flex-shrink-0" />
                <span className="line-clamp-1">{product.specs.memory}</span>
              </span>
              <span className="flex items-center gap-1">
                <Monitor className="h-4 w-4 flex-shrink-0" />
                <span className="line-clamp-1">{product.specs.display_size}</span>
              </span>
            </div>

            {/* Rating and Price */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-medium">{product.rating.toFixed(1)}</span>
                </div>
                <span className="text-xs text-muted-foreground">
                  ({product.review_count} {BRAND_CONFIG.catalog.productCard.reviews})
                </span>
                <Badge className={getAvailabilityColor(product.availability)}>
                  {getAvailabilityText(product.availability)}
                </Badge>
              </div>

              <div className="text-right">
                <div className="flex items-center gap-2">
                  {product.original_price && (
                    <span className="text-sm text-muted-foreground line-through">
                      ${product.original_price.toFixed(2)}
                    </span>
                  )}
                  <span className="text-lg font-bold text-foreground">
                    ${product.base_price.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-3 pt-2">
              <Button asChild className="flex-1">
                <Link href={`/dashboard/catalog/${product.id}`}>
                  {BRAND_CONFIG.catalog.productCard.viewDetails}
                </Link>
              </Button>
              <Button variant="outline">
                {BRAND_CONFIG.catalog.productCard.compare}
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Grid view
  return (
    <div className="bg-card border border-border rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 group">
      {/* Product Image */}
      <div className="relative aspect-[4/3] overflow-hidden">
        <Image
          src={imageError ? BRAND_CONFIG.assets.productPlaceholder : getProductImage()}
          alt={getProductImageAlt()}
          fill
          className="object-cover group-hover:scale-105 transition-transform duration-300"
          onError={() => setImageError(true)}
        />

        {/* Overlays */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />

        {/* Discount Badge */}
        {discountPercentage && (
          <Badge className="absolute top-3 left-3 bg-red-500 text-white">
            -{discountPercentage}%
          </Badge>
        )}

        {/* Wishlist Button */}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setIsWishlisted(!isWishlisted)}
          className="absolute top-3 right-3 p-2 bg-white/80 backdrop-blur-sm hover:bg-white"
        >
          <Heart className={`h-4 w-4 ${isWishlisted ? 'fill-red-500 text-red-500' : 'text-gray-700'}`} />
        </Button>

        {/* Availability Badge */}
        <Badge className={`absolute bottom-3 left-3 ${getAvailabilityColor(product.availability)}`}>
          {getAvailabilityText(product.availability)}
        </Badge>
      </div>

      {/* Product Info */}
      <div className="p-6 space-y-4">
        {/* Brand and Name */}
        <div>
          <p className="text-sm text-muted-foreground mb-1">{product.brand}</p>
          <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors overflow-hidden"
              style={{
                display: '-webkit-box',
                WebkitLineClamp: 1,
                WebkitBoxOrient: 'vertical'
              }}>
            <Link href={`/dashboard/catalog/${product.id}`}>
              {product.name}
            </Link>
          </h3>
        </div>

        {/* Key Specs */}
        <div className="space-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Cpu className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{product.specs.processor}</span>
          </div>
          <div className="flex items-center gap-2">
            <HardDrive className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{product.specs.memory} • {product.specs.storage}</span>
          </div>
          <div className="flex items-center gap-2">
            <Monitor className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{product.specs.display_size}</span>
          </div>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1">
            <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
            <span className="text-sm font-medium">{product.rating.toFixed(1)}</span>
          </div>
          <span className="text-xs text-muted-foreground">
            ({product.review_count} {BRAND_CONFIG.catalog.productCard.reviews})
          </span>
        </div>

        {/* Price */}
        <div className="space-y-1">
          {product.original_price && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground line-through">
                {BRAND_CONFIG.catalog.productCard.originalPrice}: ${product.original_price.toFixed(2)}
              </span>
              <span className="text-sm font-medium text-green-600">
                {BRAND_CONFIG.catalog.productCard.save} ${(product.original_price - product.base_price).toFixed(2)}
              </span>
            </div>
          )}
          <div className="text-2xl font-bold text-foreground">
            ${product.base_price.toFixed(2)}
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-2 pt-2">
          <Button asChild className="w-full">
            <Link href={`/dashboard/catalog/${product.id}`}>
              {BRAND_CONFIG.catalog.productCard.viewDetails}
            </Link>
          </Button>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1">
              {BRAND_CONFIG.catalog.productCard.compare}
            </Button>
            <Button variant="outline" size="sm">
              <BarChart3 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}