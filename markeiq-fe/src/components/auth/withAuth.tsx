"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppSelector, useAppDispatch } from "@/lib/redux/hooks";
import { initializeAuth } from "@/lib/redux/slices/authSlice";

export function withAuth<T extends object>(WrappedComponent: React.ComponentType<T>) {
  return function AuthenticatedComponent(props: T) {
    const router = useRouter();
    const dispatch = useAppDispatch();
    const { isAuthenticated, isLoading } = useAppSelector((state) => state.auth);

    useEffect(() => {
      // Initialize auth state
      dispatch(initializeAuth());
    }, [dispatch]);

    useEffect(() => {
      // Redirect to login if not authenticated after loading
      if (!isLoading && !isAuthenticated) {
        const currentPath = window.location.pathname;
        const redirectUrl = currentPath !== '/login' && currentPath !== '/register' 
          ? `?redirect=${encodeURIComponent(currentPath)}` 
          : '';
        router.push(`/login${redirectUrl}`);
      }
    }, [isAuthenticated, isLoading, router]);

    // Show loading while checking authentication
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading...</p>
          </div>
        </div>
      );
    }

    // Don't render if not authenticated
    if (!isAuthenticated) {
      return null;
    }

    // Render the wrapped component
    return <WrappedComponent {...props} />;
  };
}
