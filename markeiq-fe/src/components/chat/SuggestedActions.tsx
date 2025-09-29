"use client";

import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SuggestedActionsProps {
  actions: string[];
  onActionClick: (action: string) => void;
  className?: string;
}

export function SuggestedActions({ actions, onActionClick, className }: SuggestedActionsProps) {
  if (!actions || actions.length === 0) return null;

  return (
    <div className={cn("space-y-3", className)}>
      <h4 className="text-sm font-semibold text-foreground">
        Suggested Actions
      </h4>
      <div className="flex flex-wrap gap-2">
        {actions.map((action, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onActionClick(action)}
            className="text-xs h-8 px-3 hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            {action}
          </Button>
        ))}
      </div>
    </div>
  );
}
