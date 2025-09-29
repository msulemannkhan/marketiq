"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useClientOnly } from "@/hooks/useClientOnly";
import { Spinner } from "@heroui/react";

interface AuthRedirectProps {
  children: React.ReactNode;
  redirectTo?: string;
}

export function AuthRedirect({ children, redirectTo = "/dashboard" }: AuthRedirectProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();
  const mounted = useClientOnly();

  useEffect(() => {
    if (!mounted) return;
    
    // If user is authenticated, redirect to dashboard or specified route
    if (isAuthenticated && !isLoading) {
      const url = new URL(redirectTo, window.location.origin);
      const currentRedirect = new URLSearchParams(window.location.search).get('redirect');
      
      // If there's a redirect param, use that instead
      if (currentRedirect) {
        url.pathname = currentRedirect;
      }
      
      router.replace(url.toString());
    }
  }, [mounted, isAuthenticated, isLoading, router, redirectTo]);

  // Prevent hydration mismatch by not rendering until mounted
  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If authenticated, show loading while redirecting
  if (isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-muted-foreground">Redirecting...</p>
        </div>
      </div>
    );
  }

  // User is not authenticated, show the auth form
  return <>{children}</>;
}
