"use client";

import { useState, useEffect } from "react";
import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Loader } from "@/lib/components";

interface ProductSearchProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  loading?: boolean;
  className?: string;
  initialValue?: string;
}

export function ProductSearch({ 
  onSearch, 
  placeholder = "Search products...", 
  loading, 
  className,
  initialValue = ""
}: ProductSearchProps) {
  const [query, setQuery] = useState(initialValue);
  const [isFocused, setIsFocused] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Common search suggestions
  const commonSuggestions = [
    "ThinkPad", "MacBook", "Dell XPS", "HP EliteBook", "ASUS ZenBook",
    "Intel i7", "AMD Ryzen", "16GB RAM", "SSD 512GB", "4K Display"
  ];

  // Update internal state when initialValue changes
  useEffect(() => {
    setQuery(initialValue);
  }, [initialValue]);

  // Debounced search with improved logic
  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(query);

      // Update suggestions based on query
      if (query.length > 0) {
        const filteredSuggestions = commonSuggestions.filter(suggestion =>
          suggestion.toLowerCase().includes(query.toLowerCase()) &&
          suggestion.toLowerCase() !== query.toLowerCase()
        );
        setSuggestions(filteredSuggestions.slice(0, 5));
      } else {
        setSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query, onSearch]);

  const handleClear = () => {
    setQuery("");
    setShowSuggestions(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setShowSuggestions(true);
  };

  const handleFocus = () => {
    setIsFocused(true);
    setShowSuggestions(true);
  };

  const handleBlur = () => {
    // Delay hiding suggestions to allow clicking on them
    setTimeout(() => {
      setIsFocused(false);
      setShowSuggestions(false);
    }, 200);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    setShowSuggestions(false);
    onSearch(suggestion);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      setShowSuggestions(false);
      onSearch(query);
    }
    if (e.key === 'Escape') {
      setShowSuggestions(false);
      setIsFocused(false);
    }
  };

  return (
    <div className={cn("relative", className)}>
      <div className={cn(
        "relative flex items-center bg-card border border-border rounded-2xl transition-all duration-200",
        isFocused && "ring-2 ring-primary/20 border-primary/30"
      )}>
        {/* Search Icon */}
        <div className="absolute left-4 flex items-center">
          {loading ? (
            <Loader />
          ) : (
            <Search className="h-5 w-5 text-muted-foreground" />
          )}
        </div>

        {/* Input */}
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleFocus}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full pl-12 pr-12 py-4 bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none text-lg"
          disabled={loading}
        />

        {/* Clear Button */}
        {query && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="absolute right-2 p-2 hover:bg-muted rounded-xl"
            disabled={loading}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Search Suggestions */}
      {showSuggestions && isFocused && (query.length > 0 || suggestions.length > 0) && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-2xl shadow-lg z-50 max-h-64 overflow-y-auto">
          {suggestions.length > 0 ? (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-muted-foreground border-b border-border">
                Suggestions
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors flex items-center gap-2"
                >
                  <Search className="h-3 w-3 text-muted-foreground" />
                  {suggestion}
                </button>
              ))}
            </div>
          ) : query.length > 0 ? (
            <div className="p-4">
              <p className="text-sm text-muted-foreground">
                Press Enter to search for &quot;{query}&quot;
              </p>
            </div>
          ) : (
            <div className="py-2">
              <div className="px-4 py-2 text-xs font-medium text-muted-foreground border-b border-border">
                Popular Searches
              </div>
              {commonSuggestions.slice(0, 5).map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-muted transition-colors flex items-center gap-2"
                >
                  <Search className="h-3 w-3 text-muted-foreground" />
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}