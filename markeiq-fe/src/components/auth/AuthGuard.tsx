"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppDispatch } from "@/lib/redux/hooks";
import { getCurrentUser } from "@/lib/redux/slices/authSlice";
import { useAuth } from "@/hooks/useAuth";
import { Spinner } from "@heroui/react";
import { useClientOnly } from "@/hooks/useClientOnly";

interface AuthGuardProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export function AuthGuard({ children, fallback }: AuthGuardProps) {
  const router = useRouter();
  const dispatch = useAppDispatch();
  const { isAuthenticated, isLoading, user, checkTokenValidity, refreshAuthToken } = useAuth();
  const mounted = useClientOnly();
  const [hasRedirected, setHasRedirected] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Fetch current user after mount when authenticated and user missing
  useEffect(() => {
    if (!mounted) return;
    if (isAuthenticated && !user && !isRefreshing) {
      dispatch(getCurrentUser());
    }
  }, [mounted, isAuthenticated, user, dispatch, isRefreshing]);

  // Check token validity and refresh if needed
  useEffect(() => {
    if (!mounted || !isAuthenticated) return;
    
    const checkAndRefresh = async () => {
      const isValid = checkTokenValidity();
      if (!isValid) {
        setIsRefreshing(true);
        const refreshed = await refreshAuthToken();
        setIsRefreshing(false);
        if (!refreshed) {
          // Refresh failed, user will be logged out
          return;
        }
      }
    };
    
    // Check immediately
    checkAndRefresh();
    
    // Check every minute
    const interval = setInterval(checkAndRefresh, 60000);
    
    return () => clearInterval(interval);
  }, [mounted, isAuthenticated, checkTokenValidity, refreshAuthToken]);

  useEffect(() => {
    // If auth is initialized and user is not authenticated, redirect to login
    if (mounted && !isLoading && !isRefreshing && !isAuthenticated && !hasRedirected) {
      const currentPath = window.location.pathname;
      const redirectUrl = currentPath !== '/login' && currentPath !== '/register' 
        ? `?redirect=${encodeURIComponent(currentPath)}` 
        : '';
      setHasRedirected(true);
      router.push(`/login${redirectUrl}`);
    }
  }, [mounted, isLoading, isRefreshing, isAuthenticated, router, hasRedirected]);

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

  // Show loading spinner while initializing or refreshing
  if (isLoading || isRefreshing) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-muted-foreground">
            {isRefreshing ? "Refreshing session..." : "Loading..."}
          </p>
        </div>
      </div>
    );
  }

  // Show fallback or redirect if not authenticated
  if (!isAuthenticated) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-muted-foreground">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}
