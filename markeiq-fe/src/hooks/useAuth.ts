import { useEffect, useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '@/lib/redux/hooks';
import { initializeAuth, refreshToken, forceLogout, updateLastActivity } from '@/lib/redux/slices/authSlice';
import { AuthService } from '@/services/auth/auth';

export function useAuth() {
  const dispatch = useAppDispatch();
  const { 
    isAuthenticated, 
    isLoading, 
    user, 
    accessToken, 
    refreshToken: storedRefreshToken,
    error 
  } = useAppSelector((state) => state.auth);

  // Initialize auth state on mount
  useEffect(() => {
    dispatch(initializeAuth());
  }, [dispatch]);

  // Update last activity on user interaction
  const updateActivity = useCallback(() => {
    dispatch(updateLastActivity());
  }, [dispatch]);

  // Check if token needs refresh
  const checkTokenValidity = useCallback(() => {
    if (!accessToken) return false;
    
    try {
      const parts = accessToken.split('.');
      if (parts.length !== 3) return false;
      
      const payload = JSON.parse(atob(parts[1]));
      const now = Math.floor(Date.now() / 1000);
      const timeUntilExpiry = payload.exp - now;
      
      // Return true if token is valid for at least 5 minutes
      return timeUntilExpiry > 300;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }, [accessToken]);

  // Refresh token if needed
  const refreshAuthToken = useCallback(async () => {
    if (!storedRefreshToken) return false;
    
    try {
      const result = await dispatch(refreshToken({ refresh_token: storedRefreshToken }));
      return refreshToken.fulfilled.match(result);
    } catch (error) {
      console.error('Token refresh error:', error);
      dispatch(forceLogout());
      return false;
    }
  }, [storedRefreshToken, dispatch]);

  // Check if user should be logged out due to inactivity
  const checkInactivity = useCallback(() => {
    if (!isAuthenticated) return;
    
    const lastActivity = AuthService.getLastActivity();
    if (!lastActivity) return;
    
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivity;
    
    // If user is remembered, logout after 7 days of inactivity
    // If not remembered, logout after 2 days of inactivity
    const maxInactiveTime = AuthService.isRemembered() ? 7 * 24 * 60 * 60 * 1000 : 2 * 24 * 60 * 60 * 1000;
    
    if (timeSinceLastActivity > maxInactiveTime) {
      dispatch(forceLogout());
    }
  }, [isAuthenticated, dispatch]);

  // Set up activity tracking
  useEffect(() => {
    if (!isAuthenticated) return;
    
    const handleActivity = () => {
      updateActivity();
    };
    
    // Track various user activities
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    events.forEach(event => {
      document.addEventListener(event, handleActivity, true);
    });
    
    // Check inactivity every 5 minutes
    const inactivityInterval = setInterval(checkInactivity, 5 * 60 * 1000);
    
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, handleActivity, true);
      });
      clearInterval(inactivityInterval);
    };
  }, [isAuthenticated, updateActivity, checkInactivity]);

  return {
    isAuthenticated,
    isLoading,
    user,
    accessToken,
    error,
    checkTokenValidity,
    refreshAuthToken,
    updateActivity
  };
}
