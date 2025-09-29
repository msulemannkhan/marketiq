"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { ProductService } from "@/services/api/product";
import {
    ProductSearchResult,
    ProductFilters as ProductFiltersType,
} from "@/types/product";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { ProductGrid } from "@/components/business/catalog/ProductGrid";
import { ProductFilters } from "@/components/business/catalog/ProductFilters";
import { ProductSearch } from "@/components/business/catalog/ProductSearch";
import { ProductSorting } from "@/components/business/catalog/ProductSorting";
import { ProductPagination } from "@/components/business/catalog/ProductPagination";
import { Button } from "@/components/ui/button";
import { Filter, LayoutGrid, List } from "lucide-react";
import { Loader } from "@/lib/components";

export default function CatalogPage() {
    const [searchResult, setSearchResult] =
        useState<ProductSearchResult | null>(null);
    const [productsLoading, setProductsLoading] = useState(true);
    const [initialLoading, setInitialLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
    const [showFilters, setShowFilters] = useState(false);
    const [searchQuery, setSearchQuery] = useState("");
    const [filters, setFilters] = useState<ProductFiltersType>({});
    const [sortBy, setSortBy] = useState<string>("popularity");
    const [currentPage, setCurrentPage] = useState(1);

    // Fetch products when search params change (but not on filter changes)
    useEffect(() => {
        fetchProducts();
    }, [searchQuery, sortBy, currentPage]);

    // Note: Filter changes are now handled directly in handleFilterChange

    const fetchProducts = async (customFilters?: ProductFiltersType) => {
        try {
            // Only show products loading, not the whole page after initial load
            if (initialLoading) {
                setInitialLoading(false);
            }
            setProductsLoading(true);
            setError(null);

            // Use custom filters if provided, otherwise use current state
            const filtersToUse = customFilters !== undefined ? customFilters : filters;

            // Clean up filters - remove empty arrays and undefined values
            const cleanFilters: Partial<ProductFiltersType> = {};
            Object.entries(filtersToUse).forEach(([key, value]) => {
                const typedKey = key as keyof ProductFiltersType;
                if (Array.isArray(value) && value.length > 0) {
                    (cleanFilters as Record<string, unknown>)[typedKey] = value;
                } else if (
                    !Array.isArray(value) &&
                    value !== undefined &&
                    value !== null
                ) {
                    (cleanFilters as Record<string, unknown>)[typedKey] = value;
                }
            });

            const searchParams = {
                page: currentPage,
                limit: 12,
                sort_by: sortBy as
                    | "price_asc"
                    | "price_desc"
                    | "rating"
                    | "popularity"
                    | "newest"
                    | "name",
                query: searchQuery || undefined,
                filters: cleanFilters,
            };

            console.log("Fetching products with params:", searchParams);

            const result = await ProductService.getProducts(searchParams);
            setSearchResult(result);
        } catch (error: unknown) {
            console.error("Failed to fetch products:", error);
            if (
                error instanceof Error &&
                (error.message?.includes("403") ||
                    error.message?.includes("401"))
            ) {
                setError(
                    "Authentication required. Please login to view products."
                );
            } else {
                setError("Failed to load products. Please try again.");
            }
        } finally {
            setProductsLoading(false);
        }
    };

    const handleSearch = useCallback((query: string) => {
        setSearchQuery(query);
        setCurrentPage(1);
    }, []);

    const handleFilterChange = useCallback((newFilters: ProductFiltersType) => {
        console.log("Filters applied:", newFilters);
        setFilters(newFilters);
        setCurrentPage(1);
        // Trigger immediate fetch with new filters
        fetchProducts(newFilters);
    }, [fetchProducts]);

    const handleSortChange = useCallback((newSortBy: string) => {
        setSortBy(newSortBy);
        setCurrentPage(1);
    }, []);

    const handlePageChange = useCallback((page: number) => {
        setCurrentPage(page);
        // Scroll to top when page changes
        window.scrollTo({ top: 0, behavior: "smooth" });
    }, []);

    // Initial loading state - show full page loading
    if (initialLoading) {
        return (
            <div className="p-6 space-y-6 min-h-screen bg-background">
                <div className="flex items-center justify-center min-h-[60vh] gap-2">
                    <Loader />
                    <p className="text-muted-foreground">
                        {BRAND_CONFIG.catalog.loadingMessage}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6 min-h-screen bg-background">
            {/* Header */}
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-bold text-foreground tracking-tight">
                        {BRAND_CONFIG.catalog.title}
                    </h1>
                    <p className="mt-2 text-muted-foreground text-lg">
                        {BRAND_CONFIG.catalog.subtitle}
                    </p>
                </div>

                {/* View Mode Toggle */}
                <div className="flex items-center gap-3">
                    <div className="flex items-center bg-card border border-border rounded-xl p-1">
                        <Button
                            variant={viewMode === "grid" ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setViewMode("grid")}
                            className="rounded-lg"
                        >
                            <LayoutGrid className="h-4 w-4" />
                        </Button>
                        <Button
                            variant={viewMode === "list" ? "default" : "ghost"}
                            size="sm"
                            onClick={() => setViewMode("list")}
                            className="rounded-lg"
                        >
                            <List className="h-4 w-4" />
                        </Button>
                    </div>

                    <Button
                        variant="outline"
                        onClick={() => setShowFilters(!showFilters)}
                        className="lg:hidden"
                    >
                        <Filter className="h-4 w-4 mr-2" />
                        Filters
                    </Button>
                </div>
            </div>

            {/* Search Bar */}
            <ProductSearch
                onSearch={handleSearch}
                placeholder={BRAND_CONFIG.catalog.searchPlaceholder}
                loading={productsLoading}
                initialValue={searchQuery}
            />

            <div className="flex flex-col lg:flex-row gap-6">
                {/* Sidebar Filters - Desktop */}
                <div
                    className={`lg:w-80 ${
                        showFilters ? "block" : "hidden lg:block"
                    }`}
                >
                    <div className="bg-card border border-border rounded-2xl p-6 sticky top-6">
                        <ProductFilters
                            onFilterChange={handleFilterChange}
                            facets={searchResult?.facets}
                            loading={false} // Don't show loading for filters
                            currentFilters={filters}
                        />
                    </div>
                </div>

                {/* Main Content */}
                <div className="flex-1">
                    {/* Results Header */}
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                        <div className="text-sm text-muted-foreground">
                            {productsLoading && (
                                <span>Loading products...</span>
                            )}
                            {searchResult && !productsLoading && (
                                <span>
                                    {searchResult.total.toLocaleString()}{" "}
                                    {BRAND_CONFIG.catalog.pagination.results}{" "}
                                    found
                                </span>
                            )}
                        </div>

                        <ProductSorting
                            value={sortBy}
                            onChange={handleSortChange}
                            options={BRAND_CONFIG.catalog.sorting.options}
                        />
                    </div>

                    {/* Error State */}
                    {error && !productsLoading && (
                        <div className="text-center py-12">
                            <div className="w-16 h-16 mx-auto mb-4 bg-red-100 dark:bg-red-500/20 rounded-full flex items-center justify-center">
                                <Filter className="h-8 w-8 text-red-500 dark:text-red-400" />
                            </div>
                            <h3 className="text-xl font-semibold text-foreground mb-2">
                                Connection Issue
                            </h3>
                            <p className="text-muted-foreground mb-6">
                                {error}
                            </p>
                            <Button onClick={() => fetchProducts()}>
                                Try Again
                            </Button>
                        </div>
                    )}

                    {/* No Results */}
                    {searchResult &&
                        searchResult.products.length === 0 &&
                        !productsLoading &&
                        !error && (
                            <div className="text-center py-12">
                                <div className="text-muted-foreground mb-4">
                                    {BRAND_CONFIG.catalog.noResults}
                                </div>
                                <Button
                                    onClick={() => {
                                        setSearchQuery("");
                                        setFilters({});
                                        setCurrentPage(1);
                                    }}
                                >
                                    Clear All Filters
                                </Button>
                            </div>
                        )}

                    {/* Products Grid */}
                    <ProductGrid
                        products={searchResult?.products || []}
                        viewMode={viewMode}
                        loading={productsLoading}
                    />

                    {/* Pagination */}
                    <ProductPagination
                        searchResult={searchResult}
                        currentPage={currentPage}
                        onPageChange={handlePageChange}
                        loading={productsLoading}
                    />
                </div>
            </div>
        </div>
    );
}
