"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { ProductService } from "@/services/api/product";
import { AuthService } from "@/services/auth/auth";
import { Product } from "@/types/product";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import {
    Star,
    Heart,
    Share2,
    ShoppingCart,
    ArrowLeft,
    ChevronLeft,
    ChevronRight,
    Cpu,
    HardDrive,
    Monitor,
    Battery,
    Laptop,
    ExternalLink
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { Loader } from "@/lib/components";

export default function ProductDetailPage() {
    const { id } = useParams<{ id: string }>();

    const [product, setProduct] = useState<Product | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);
    const [isWishlisted, setIsWishlisted] = useState(false);
    const [imageError, setImageError] = useState(false);

    // Check authentication
    useEffect(() => {
        setIsAuthenticated(AuthService.isAuthenticated());
    }, []);

    // Fetch product details
    useEffect(() => {
        if (isAuthenticated && id) {
            fetchProductDetails();
        }
    }, [isAuthenticated, id]);

    const fetchProductDetails = async () => {
        try {
            setLoading(true);
            setError(null);
            console.log('Fetching product details for ID:', id);
            const productData = await ProductService.getProduct(id);
            console.log('Product data received:', productData);
            setProduct(productData);
        } catch (error) {
            console.error("Failed to fetch product details:", error);
            if (error instanceof Error) {
                if (error.message?.includes('404')) {
                    setError("Product not found. Please check the URL and try again.");
                } else if (error.message?.includes('403') || error.message?.includes('401')) {
                    setError("Authentication required. Please login to view product details.");
                } else {
                    setError(`Failed to load product details: ${error.message}`);
                }
            } else {
            setError("Failed to load product details. Please try again.");
            }
        } finally {
            setLoading(false);
        }
    };

    // Loading state
    if (loading) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <div className="flex items-center gap-3">
                    <Loader />
                    <p className="text-muted-foreground">Loading product details...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error || !product) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <Card className="max-w-md w-full">
                    <CardContent className="pt-6 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 bg-destructive/10 rounded-full flex items-center justify-center">
                            <Laptop className="h-8 w-8 text-destructive" />
                    </div>
                        <h3 className="text-xl font-semibold mb-2">Product Not Found</h3>
                    <p className="text-muted-foreground mb-6">
                            {error || "The product you are looking for could not be found."}
                    </p>
                    <Button asChild>
                        <Link href="/dashboard/catalog">
                            <ArrowLeft className="h-4 w-4 mr-2" />
                            Back to Catalog
                        </Link>
                    </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Authentication check
    if (!isAuthenticated) {
        return (
            <div className="min-h-screen bg-background flex items-center justify-center">
                <Card className="max-w-md w-full">
                    <CardContent className="pt-6 text-center">
                        <div className="w-16 h-16 mx-auto mb-4 bg-primary/10 rounded-full flex items-center justify-center">
                            <Laptop className="h-8 w-8 text-primary" />
                    </div>
                        <h3 className="text-xl font-semibold mb-2">Authentication Required</h3>
                    <p className="text-muted-foreground mb-6">
                        Please login to view product details and specifications.
                    </p>
                    <Button asChild>
                        <Link href="/login">Go to Login</Link>
                    </Button>
                    </CardContent>
                </Card>
            </div>
        );
    }

    // Get images from product_images array or fallback to image_url
    const getProductImages = () => {
        if (product.product_images && product.product_images.length > 0) {
            return product.product_images.map(img => img.url);
        }
        return product.image_url ? [product.image_url] : [];
    };

    const images = getProductImages();
    const currentImage = images[currentImageIndex] || BRAND_CONFIG.assets.productPlaceholder;
    const discountPercentage = product.original_price && product.original_price > 0 // Ensure original_price is positive to avoid division by zero
        ? Math.round(((product.original_price - product.base_price) / product.original_price) * 100)
        : null;

    const getAvailabilityColor = (availability: string) => {
        switch (availability.toLowerCase()) {
            case 'available':
            case 'in stock': return 'bg-green-500/10 text-green-600 dark:text-green-400 border-green-500/20';
            case 'out of stock':
            case 'currently out of stock': return 'bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20';
            case 'pre order':
            case 'pre-order': return 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20';
            case 'limited stock':
            case 'hurry, last few remaining': return 'bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20';
            default: return 'bg-gray-500/10 text-gray-600 dark:text-gray-400 border-gray-500/20';
        }
    };

    const getAvailabilityText = (availability: string) => {
        switch (availability.toLowerCase()) {
            case 'available':
            case 'in stock': return 'In Stock';
            case 'out of stock':
            case 'currently out of stock': return 'Out of Stock';
            case 'pre order':
            case 'pre-order': return 'Pre-Order';
            case 'limited stock':
            case 'hurry, last few remaining': return 'Limited Stock';
            default: return availability;
        }
    };

    return (
        <div className="min-h-screen bg-background">
            {/* Breadcrumb Navigation */}
            <div className="border-b border-border bg-muted/30">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <nav className="flex items-center space-x-2 text-sm text-muted-foreground">
                        <Link href="/dashboard" className="hover:text-foreground transition-colors">
                            Dashboard
                        </Link>
                        <span>/</span>
                        <Link href="/dashboard/catalog" className="hover:text-foreground transition-colors">
                            Catalog
                        </Link>
                        <span>/</span>
                        <span className="text-foreground font-medium">{product.brand}</span>
                        <span>/</span>
                        <span className="text-foreground">{product.model}</span>
                    </nav>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Main Product Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-12">
                    {/* Product Images */}
                    <div className="space-y-6">
                        <Card className="overflow-hidden">
                            <CardContent className="p-0">
                                <div className="relative aspect-square">
                            <Image
                                        src={imageError ? BRAND_CONFIG.assets.productPlaceholder : currentImage}
                                alt={product.name}
                                fill
                                className="object-cover"
                                priority
                                        onError={() => setImageError(true)}
                                    />
                                    
                                    {/* Discount Badge */}
                                    {discountPercentage !== null && Math.round(discountPercentage) > 0 && (
                                        <Badge className="absolute top-4 left-4 bg-red-500 text-white z-10">
                                            -{Math.round(discountPercentage)}%
                                        </Badge>
                                    )}

                            {/* Image Navigation */}
                            {images.length > 1 && (
                                <>
                                            <Button
                                                variant="secondary"
                                                size="icon"
                                                className="absolute left-4 top-1/2 -translate-y-1/2 bg-background/80 backdrop-blur"
                                                onClick={() => setCurrentImageIndex(prev => prev === 0 ? images.length - 1 : prev - 1)}
                                    >
                                        <ChevronLeft className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="secondary"
                                                size="icon"
                                                className="absolute right-4 top-1/2 -translate-y-1/2 bg-background/80 backdrop-blur"
                                                onClick={() => setCurrentImageIndex(prev => prev === images.length - 1 ? 0 : prev + 1)}
                                    >
                                        <ChevronRight className="h-4 w-4" />
                                            </Button>
                                </>
                            )}
                        </div>
                            </CardContent>
                        </Card>

                        {/* Thumbnail Images */}
                        {images.length > 1 && (
                            <div className="flex gap-4 overflow-x-auto">
                                {images.map((image, index) => (
                                    <button
                                        key={index}
                                        onClick={() => setCurrentImageIndex(index)}
                                        className={`relative w-20 h-20 rounded-lg overflow-hidden border-2 flex-shrink-0 transition-all ${
                                            index === currentImageIndex
                                                ? "border-primary ring-2 ring-primary/20" 
                                                : "border-border hover:border-muted-foreground"
                                        }`}
                                    >
                                        <Image
                                            src={image}
                                            alt={`${product.name} view ${index + 1}`}
                                            fill
                                            className="object-cover"
                                            onError={() => setImageError(true)}
                                        />
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Product Information */}
                    <div className="space-y-8">
                        {/* Header */}
                        <div className="space-y-4">
                            <div className="flex items-center gap-2 flex-wrap">
                                <Badge variant="secondary">{product.brand}</Badge>
                                <Badge variant="outline">{product.model}</Badge>
                                <Badge className={getAvailabilityColor(product.availability)}>
                                    {getAvailabilityText(product.availability)}
                                </Badge>
                            </div>

                            <h1 className="text-3xl font-bold text-foreground leading-tight">
                                {product.name}
                            </h1>
                        </div>

                        {/* Pricing */}
                        <div className="space-y-3">
                            {product.original_price && product.original_price > product.base_price && (
                                <div className="flex items-center gap-4">
                                    <span className="text-xl text-muted-foreground line-through">
                                        ${product.original_price.toFixed(2)}
                                    </span>
                                    <span className="text-lg font-medium text-green-600 dark:text-green-400">
                                        Save ${(product.original_price - product.base_price).toFixed(2)}
                                    </span>
                                </div>
                            )}
                            <div className="text-4xl font-bold text-foreground">
                                {product.base_price === 0 ? "Free" : `$${product.base_price.toFixed(2)}`}
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4">
                            <Button 
                                size="lg" 
                                className="flex-1"
                                disabled={product.availability.toLowerCase().includes('out of stock')}
                            >
                                <ShoppingCart className="h-5 w-5 mr-2" />
                                {product.availability.toLowerCase().includes('out of stock') ? "Out of Stock" : "Add to Cart"}
                            </Button>
                            
                            <div className="flex gap-2">
                                <Button
                                    variant="outline"
                                    size="lg"
                                    onClick={() => setIsWishlisted(!isWishlisted)}
                                >
                                    <Heart className={`h-5 w-5 ${isWishlisted ? "fill-red-500 text-red-500" : ""}`} />
                                </Button>
                                <Button variant="outline" size="lg">
                                    <Share2 className="h-5 w-5" />
                                </Button>
                            </div>
                        </div>

                        {/* Rating */}
                        <div className="flex items-center gap-2">
                            {product.review_count > 0 ? (
                                <>
                                    <div className="flex items-center gap-1">
                                        {[...Array(5)].map((_, i) => (
                                            <Star
                                                key={i}
                                                className={`h-5 w-5 ${
                                                    i < Math.floor(product.rating)
                                                        ? "fill-yellow-400 text-yellow-400"
                                                        : "text-gray-300"
                                                }`}
                                            />
                                        ))}
                                        <span className="font-medium ml-2">
                                            {product.rating.toFixed(1)}
                                        </span>
                                    </div>
                                    <span className="text-muted-foreground">
                                        ({product.review_count} reviews)
                                    </span>
                                </>
                            ) : (
                                <span className="text-muted-foreground">No ratings yet</span>
                            )}
                        </div>

                        {/* Description */}
                        {product.description && (
                        <div className="prose prose-gray dark:prose-invert max-w-none">
                            <p className="text-muted-foreground leading-relaxed">
                                {product.description}
                            </p>
                        </div>
                        )}

                        {/* Key Specifications */}
                        <Card>
                            <CardContent className="pt-6">
                                <h3 className="text-lg font-semibold mb-4">Key Specifications</h3>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <Cpu className="h-5 w-5 text-foreground" />
                        </div>
                                        <div>
                                            <div className="font-medium text-sm">Processor</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.processor}</div>
                    </div>
                </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <HardDrive className="h-5 w-5 text-foreground" />
                                </div>
                                        <div>
                                            <div className="font-medium text-sm">Memory</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.memory}</div>
                            </div>
                        </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <HardDrive className="h-5 w-5 text-foreground" />
                                </div>
                                        <div>
                                            <div className="font-medium text-sm">Storage</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.storage}</div>
                            </div>
                        </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <Monitor className="h-5 w-5 text-foreground" />
                                </div>
                                        <div>
                                            <div className="font-medium text-sm">Display</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.display}</div>
                            </div>
                        </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <Laptop className="h-5 w-5 text-foreground" />
                                </div>
                                        <div>
                                            <div className="font-medium text-sm">Graphics</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.graphics}</div>
                        </div>
                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-muted rounded-lg">
                                            <Battery className="h-5 w-5 text-foreground" />
                                        </div>
                                        <div>
                                            <div className="font-medium text-sm">Battery</div>
                                            <div className="text-sm text-muted-foreground">{product.specs.battery}</div>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        {/* Additional Information */}
                        <div className="space-y-4">
                            {product.pdf_spec_url && (
                                <Button variant="outline" asChild className="w-full">
                                    <a href={product.pdf_spec_url} target="_blank" rel="noopener noreferrer">
                                        <ExternalLink className="h-4 w-4 mr-2" />
                                        Download Technical Specifications PDF
                                    </a>
                                </Button>
                            )}
                            </div>
                    </div>
                </div>
            </div>
        </div>
    );
}