"use client";

import { useClientOnly } from "@/hooks/useClientOnly";

interface ClientOnlyProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * Component that only renders its children on the client side to prevent hydration mismatches
 */
export function ClientOnly({ children, fallback = null }: ClientOnlyProps) {
  const mounted = useClientOnly();

  if (!mounted) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
