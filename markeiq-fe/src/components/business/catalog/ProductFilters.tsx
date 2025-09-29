"use client";

import { useState, useEffect } from "react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";
import { ProductFilters as ProductFiltersType } from "@/types/product";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@heroui/react";
import { ChevronDown, ChevronUp, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ProductFiltersProps {
  onFilterChange: (filters: ProductFiltersType) => void;
  facets?: {
    brands: { name: string; count: number }[];
    price_ranges: { min: number; max: number; count: number }[];
    processors: { name: string; count: number }[];
    memory: { name: string; count: number }[];
    storage: { name: string; count: number }[];
  };
  loading?: boolean;
  currentFilters?: ProductFiltersType;
}

export function ProductFilters({ onFilterChange, facets, loading, currentFilters = {} }: ProductFiltersProps) {
  const [filters, setFilters] = useState<ProductFiltersType>(currentFilters);
  const [appliedFilters, setAppliedFilters] = useState<ProductFiltersType>(currentFilters);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    brands: true,
    price: true,
    processor: true,
    memory: true,
    storage: true,
    rating: true,
    availability: true
  });

  // Initialize price range from facets or use defaults
  const getInitialPriceRange = (): [number, number] => {
    if (currentFilters.price_min !== undefined || currentFilters.price_max !== undefined) {
      return [currentFilters.price_min || 0, currentFilters.price_max || 5000];
    }
    if (facets?.price_ranges && facets.price_ranges.length > 0) {
      const minPrice = Math.min(...facets.price_ranges.map(p => p.min));
      const maxPrice = Math.max(...facets.price_ranges.map(p => p.max));
      return [minPrice, maxPrice];
    }
    return [0, 5000];
  };

  const [priceRange, setPriceRange] = useState<[number, number]>(getInitialPriceRange());

  // Update internal state when external filters change
  useEffect(() => {
    setFilters(currentFilters);
    setAppliedFilters(currentFilters); // Ensure appliedFilters also syncs with external changes
    const newPriceRange = getInitialPriceRange();
    setPriceRange(newPriceRange);
  }, [currentFilters, facets]);

  // Simplified filter update function - only stage changes, don't apply
  const updateFilter = (key: keyof ProductFiltersType, value: ProductFiltersType[keyof ProductFiltersType]) => {
    const newFilters: ProductFiltersType = { ...filters };
    
    if (value === undefined || value === null || (Array.isArray(value) && value.length === 0)) {
      delete newFilters[key];
    } else {
      newFilters[key] = value as (string | string[]) & number;
    }

    console.log('Filter staged:', key, value);
    setFilters(newFilters);
    // Don't auto-apply - wait for Apply button
  };

  // Handle price range changes - always set price values
  const handlePriceChange = (newRange: [number, number]) => {
    const newFilters = { ...filters };
    const [min, max] = newRange;
    
    // Always set price values - let backend handle the logic
    newFilters.price_min = min;
    newFilters.price_max = max;

    console.log('Price range staged:', { min, max, filters: newFilters });
    setFilters(newFilters);
    // Don't auto-apply - wait for Apply button
  };

  const removeFilter = (key: keyof ProductFiltersType, value?: string) => {
    if (key === 'price_min' || key === 'price_max') {
      // Reset price range to full range
      const fullRange = getInitialPriceRange();
      setPriceRange(fullRange);
      
      const newFilters = { ...filters };
      delete newFilters.price_min;
      delete newFilters.price_max;
      
      setFilters(newFilters);
      // Don't auto-apply - wait for Apply button
    } else if (value && Array.isArray(filters[key])) {
      const currentValues = filters[key] as string[];
      const newValues = currentValues.filter(v => v !== value);
      updateFilter(key, newValues.length > 0 ? newValues : undefined);
    } else {
      updateFilter(key, undefined);
    }
  };

  const clearAllFilters = () => {
    const initialRange = getInitialPriceRange();
    setPriceRange(initialRange);
    setFilters({});
    setAppliedFilters({}); // Also clear applied filters
    onFilterChange({}); // Immediately fetch products with no filters
  };

  const applyFilters = () => {
    console.log('Applying filters:', filters);
    setAppliedFilters(filters);
    // Emit filters to parent to trigger backend query
    onFilterChange(filters);
  };

  const applyQuickFilter = (quickFilter: { name: string; filters: Partial<ProductFiltersType> }) => {
    console.log('Quick filter staged:', quickFilter.name, quickFilter.filters);
    
    // Update price range if needed
    if (quickFilter.filters.price_min !== undefined || quickFilter.filters.price_max !== undefined) {
      const fullRange = getInitialPriceRange();
      setPriceRange([
        quickFilter.filters.price_min || fullRange[0],
        quickFilter.filters.price_max || fullRange[1]
      ]);
    }
    
    setFilters(quickFilter.filters);
    // Don't auto-apply - wait for Apply button
  };

  const quickFilters = [
    {
      name: "Budget Friendly",
      filters: { price_max: 800 }
    },
    {
      name: "Premium",
      filters: { price_min: 1500, brands: ["Apple", "Dell"] }
    },
    {
      name: "Gaming Ready",
      filters: { processors: ["Intel Core i7", "AMD Ryzen 7"], memory: ["16GB", "32GB"] }
    },
    {
      name: "Business",
      filters: { brands: ["HP", "Lenovo", "Dell"], processors: ["Intel Core i5", "Intel Core i7"] }
    }
  ];

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const FilterSection = ({
    title,
    section,
    children
  }: {
    title: string;
    section: string;
    children: React.ReactNode;
  }) => (
    <div className="border-b border-border pb-4 last:border-b-0">
      <button
        onClick={() => toggleSection(section)}
        className="flex items-center justify-between w-full py-2 text-left"
      >
        <h3 className="font-medium text-foreground">{title}</h3>
        {expandedSections[section] ? (
          <ChevronUp className="h-4 w-4 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        )}
      </button>
      {expandedSections[section] && (
        <div className="mt-3 space-y-3">
          {children}
        </div>
      )}
    </div>
  );

  const CheckboxFilter = ({
    options,
    selectedValues = [],
    onChange,
    showCount = true
  }: {
    options: { name: string; count?: number }[];
    selectedValues?: string[];
    onChange: (values: string[]) => void;
    showCount?: boolean;
  }) => (
    <ScrollArea className="h-fit max-h-48 overflow-y-auto w-full scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent"> {/* Replaced div with ScrollArea, added border and pr-4 for scrollbar */}
      <div className="space-y-2 p-1"> {/* Added a div inside ScrollArea for consistent spacing */}
        {options.map((option) => (
          <label
            key={option.name}
            className="flex items-center justify-between cursor-pointer group"
          >
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedValues.includes(option.name)}
                onChange={(e) => {
                  const newValues = e.target.checked
                    ? [...selectedValues, option.name]
                    : selectedValues.filter(v => v !== option.name);
                  onChange(newValues);
                }}
                className="rounded border-border text-primary focus:ring-primary focus:ring-offset-0 focus:ring-2"
              />
              <span className="text-sm text-foreground group-hover:text-primary transition-colors line-clamp-1">
                {option.name}
              </span>
            </div>
            {showCount && option.count && (
              <span className="text-xs text-muted-foreground">
                {option.count}
              </span>
            )}
          </label>
        ))}
      </div>
    </ScrollArea>
  );

  // Get active filter count
  const activeFilterCount = Object.entries(filters).reduce((count, [key, value]) => {
    if (Array.isArray(value) && value.length > 0) return count + value.length;
    if (value !== undefined && value !== null && key !== 'price_min' && key !== 'price_max') return count + 1;
    return count;
  }, 0) + (filters.price_min !== undefined || filters.price_max !== undefined ? 1 : 0);

  // Check if there are any staged changes
  const hasStagedChanges = JSON.stringify(filters) !== JSON.stringify(appliedFilters);
  
  console.log('Filter states:', {
    hasStagedChanges,
    filters,
    appliedFilters
  });

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-3 pb-4 border-b border-border last:border-b-0">
              <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
              <div className="space-y-2">
                {[...Array(3)].map((_, j) => (
                  <div key={j} className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
          {BRAND_CONFIG.catalog.filters.title}
          {activeFilterCount > 0 && (
            <Badge variant="secondary" className="ml-2">
              {activeFilterCount}
            </Badge>
          )}
          {hasStagedChanges && (
            <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse" title="Pending changes"></div>
          )}
        </h2>
        <div className="flex items-center gap-2">
          {activeFilterCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearAllFilters}
              className="text-xs"
            >
              {BRAND_CONFIG.catalog.filters.clearAll}
            </Button>
          )}
          <Button
            variant="default"
            size="sm"
            onClick={applyFilters}
            className="text-xs"
          >
            Apply
          </Button>
        </div>
      </div>

      {/* Quick Filters */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-foreground">Quick Filters</h3>
        <div className="flex flex-wrap gap-2">
          {quickFilters.map((quickFilter) => (
            <Button
              key={quickFilter.name}
              variant="outline"
              size="sm"
              onClick={() => applyQuickFilter(quickFilter)}
              className="text-xs h-8"
            >
              {quickFilter.name}
            </Button>
          ))}
        </div>
      </div>

      {/* Active Filters */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap gap-2">
          {filters.brands?.map(brand => (
            <Badge key={brand} variant="secondary" className="flex items-center gap-1">
              {brand}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('brands', brand)}
              />
            </Badge>
          ))}
          {filters.processors?.map(processor => (
            <Badge key={processor} variant="secondary" className="flex items-center gap-1">
              {processor}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('processors', processor)}
              />
            </Badge>
          ))}
          {filters.memory?.map(memory => (
            <Badge key={memory} variant="secondary" className="flex items-center gap-1">
              {memory}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('memory', memory)}
              />
            </Badge>
          ))}
          {filters.storage?.map(storage => (
            <Badge key={storage} variant="secondary" className="flex items-center gap-1">
              {storage}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('storage', storage)}
              />
            </Badge>
          ))}
          {(filters.price_min !== undefined || filters.price_max !== undefined) && (
            <Badge variant="secondary" className="flex items-center gap-1">
              ${filters.price_min || 0} - ${filters.price_max || 5000}
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('price_min')}
              />
            </Badge>
          )}
          {filters.ratings && (
            <Badge variant="secondary" className="flex items-center gap-1">
              {filters.ratings}+ stars
              <X
                className="h-3 w-3 cursor-pointer hover:text-destructive"
                onClick={() => removeFilter('ratings')}
              />
            </Badge>
          )}
        </div>
      )}

      {/* Brand Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.brand} section="brands">
        <CheckboxFilter
          options={facets?.brands || [
            { name: "HP", count: 15 },
            { name: "Lenovo", count: 12 },
            { name: "Dell", count: 8 },
            { name: "ASUS", count: 6 }
          ]}
          selectedValues={filters.brands || []}
          onChange={(values) => updateFilter('brands', values.length > 0 ? values : undefined)}
        />
      </FilterSection>

      {/* Price Range Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.priceRange} section="price">
        <div className="space-y-4">
          <Slider
            className="max-w-full"
            formatOptions={{style: "currency", currency: "USD"}}
            label="Select price range"
            maxValue={5000}
            minValue={0}
            step={50}
            value={priceRange}
            onChange={(value) => {
              const newRange = value as [number, number];
              setPriceRange(newRange);
              handlePriceChange(newRange);
            }}
          />
          <p className="text-default-500 font-medium text-small">
            Selected range: ${priceRange[0]} – ${priceRange[1]}
          </p>
        </div>
      </FilterSection>

      {/* Processor Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.processor} section="processor">
        <CheckboxFilter
          options={facets?.processors || [
            { name: "Intel Core i5", count: 8 },
            { name: "Intel Core i7", count: 12 },
            { name: "AMD Ryzen 5", count: 6 },
            { name: "AMD Ryzen 7", count: 4 }
          ]}
          selectedValues={filters.processors || []}
          onChange={(values) => updateFilter('processors', values.length > 0 ? values : undefined)}
        />
      </FilterSection>

      {/* Memory Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.memory} section="memory">
        <CheckboxFilter
          options={facets?.memory || [
            { name: "8GB", count: 10 },
            { name: "16GB", count: 15 },
            { name: "32GB", count: 5 }
          ]}
          selectedValues={filters.memory || []}
          onChange={(values) => updateFilter('memory', values.length > 0 ? values : undefined)}
        />
      </FilterSection>

      {/* Storage Filter */}
      <FilterSection title="Storage" section="storage">
        <CheckboxFilter
          options={facets?.storage || [
            { name: "256GB SSD", count: 8 },
            { name: "512GB SSD", count: 12 },
            { name: "1TB SSD", count: 6 },
            { name: "2TB SSD", count: 3 }
          ]}
          selectedValues={filters.storage || []}
          onChange={(values) => updateFilter('storage', values.length > 0 ? values : undefined)}
        />
      </FilterSection>

      {/* Rating Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.rating} section="rating">
        <div className="space-y-2">
          {[4, 3, 2, 1].map((rating) => (
            <label key={rating} className="flex items-center gap-2 cursor-pointer">
              <input
                type="radio"
                name="rating"
                checked={filters.ratings === rating}
                onChange={() => updateFilter('ratings', rating)}
                className="text-primary focus:ring-primary"
              />
              <span className="text-sm">
                {rating}+ stars
              </span>
            </label>
          ))}
        </div>
      </FilterSection>

      {/* Availability Filter */}
      <FilterSection title={BRAND_CONFIG.catalog.filters.availability} section="availability">
        <CheckboxFilter
          options={[
            { name: "in_stock" },
            { name: "pre_order" },
            { name: "coming_soon" }
          ]}
          selectedValues={filters.availability || []}
          onChange={(values) => updateFilter('availability', values.length > 0 ? values : undefined)}
          showCount={false}
        />
      </FilterSection>
    </div>
  );
}