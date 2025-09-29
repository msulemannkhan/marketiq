import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Define protected routes
const protectedRoutes = ['/dashboard'];
const authRoutes = ['/login', '/register'];

function clearAuthCookies(response: NextResponse) {
  // Clear all possible auth cookie variations
  response.cookies.set('auth_token', '', {
    expires: new Date(0),
    path: '/',
    httpOnly: false,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax'
  });
  response.cookies.set('auth_token', '', {
    expires: new Date(0),
    path: '/',
    httpOnly: false,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  });
  response.cookies.set('auth_token', '', {
    expires: new Date(0),
    path: '/',
    httpOnly: false,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'none'
  });
  return response;
}

function isTokenValid(token: string): boolean {
  try {
    // Basic JWT token validation - check if it's a valid JWT format
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }
    
    // Check if token is expired (basic check)
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    // Check if token has expired
    if (payload.exp && payload.exp < now) {
      return false;
    }
    
    // Check if token has required fields
    if (!payload.sub || !payload.iat) {
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
}

function isTokenExpired(token: string): boolean {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    // Add 5 minute buffer for token refresh
    return payload.exp && payload.exp < (now + 300);
  } catch (error) {
    return true;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );
  const isAuthRoute = authRoutes.some((route) =>
    pathname.startsWith(route)
  );

  // Get auth token from cookies
  const token = request.cookies.get('auth_token')?.value;

  // Block access to protected routes if not authenticated
  if (isProtectedRoute) {
    if (!token) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Check if token is valid and not expired
    if (!isTokenValid(token)) {
      const response = NextResponse.redirect(new URL('/login', request.url));
      return clearAuthCookies(response);
    }

    // If token is close to expiring, let the client handle refresh
    // Don't block access, just let the client-side refresh logic handle it
  }

  // Prevent logged-in users from accessing login/register
  if (isAuthRoute && token && isTokenValid(token)) {
    const redirectTo =
      request.nextUrl.searchParams.get('redirect') || '/dashboard';
    return NextResponse.redirect(new URL(redirectTo, request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/(auth)/login', '/(auth)/register'],
};
