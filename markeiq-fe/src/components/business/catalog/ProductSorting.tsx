"use client";

import { ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";
import { BRAND_CONFIG } from "@/lib/config/brand-config";

interface ProductSortingProps {
  value: string;
  onChange: (value: string) => void;
  options: Record<string, string>;
}

export function ProductSorting({ value, onChange, options }: ProductSortingProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentLabel = options[value] || value;

  return (
    <div className="relative" ref={dropdownRef}>
      <Button
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 min-w-[180px] justify-between"
      >
        <span className="text-sm">
          {BRAND_CONFIG.catalog.sorting.label}: {currentLabel}
        </span>
        <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && (
        <div className="absolute top-full right-0 mt-2 w-56 bg-card border border-border rounded-xl shadow-lg z-50 py-2">
          {Object.entries(options).map(([optionValue, optionLabel]) => (
            <button
              key={optionValue}
              onClick={() => {
                onChange(optionValue);
                setIsOpen(false);
              }}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors ${
                value === optionValue ? 'bg-muted font-medium' : ''
              }`}
            >
              {optionLabel}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}