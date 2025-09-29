"use client";

import { Citation } from '@/types/chat';
import { ExternalLink, Database, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CitationsProps {
  citations: Citation[];
  className?: string;
}

export function Citations({ citations, className }: CitationsProps) {
  if (!citations || citations.length === 0) return null;

  const getSourceIcon = (productName: string) => {
    switch (productName.toLowerCase()) {
      case 'product_catalog':
        return <Database className="h-3 w-3" />;
      case 'canonical_specs':
        return <FileText className="h-3 w-3" />;
      default:
        return <ExternalLink className="h-3 w-3" />;
    }
  };

  const getSourceLabel = (productName: string) => {
    return productName;
  };

  return (
    <div className={cn("space-y-3", className)}>
      <h4 className="text-sm font-semibold text-foreground">
        Sources
      </h4>
      <div className="space-y-2">
        {citations.map((citation, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-muted/50 rounded-lg border"
          >
            <div className="flex items-center gap-2 flex-1 min-w-0">
              {getSourceIcon(citation.product_name)}
              <span className="text-sm font-medium text-foreground">
                {getSourceLabel(citation.product_name)}
              </span>
              <span className="text-xs text-muted-foreground">
                SKU: {citation.sku}
              </span>
              {citation.url && (
                <a
                  href={citation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
            <div className="flex items-center gap-2 ml-4">
              <div className="text-xs text-muted-foreground">
                {Math.round(citation.relevance_score * 100)}% relevant
              </div>
              <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${citation.relevance_score * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
