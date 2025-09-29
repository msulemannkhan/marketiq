"use client";

import { useEffect } from "react";
import { useAppDispatch } from "@/lib/redux/hooks";
import { initializeAuth } from "@/lib/redux/slices/authSlice";
import { useClientOnly } from "@/hooks/useClientOnly";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const dispatch = useAppDispatch();
  const mounted = useClientOnly();

  useEffect(() => {
    if (!mounted) return;
    
    // Initialize auth state from localStorage/sessionStorage
    dispatch(initializeAuth());
  }, [dispatch, mounted]);

  return <>{children}</>;
}
