import { AuthService, ApiError } from "./auth/auth"; // NOTE: Importing ApiError from auth.ts creates a circular dependency as auth.ts imports makeRequest.
                                                  // ApiError should ideally be moved to a shared types/errors file (e.g., src/types/api.ts or src/services/api-error.ts)
                                                  // to break this dependency.

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export const makeRequest = async <T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> => {
    // 1. Validate API_BASE_URL
    if (!API_BASE_URL) {
      throw new Error('API_BASE_URL is not defined. Please set NEXT_PUBLIC_API_BASE_URL environment variable.');
    }

    const token = AuthService.getAuthToken();
    const url = `${API_BASE_URL}${endpoint}`;

    // 2. Robust Header Handling
    // Start with user-provided headers, then apply defaults/auth, allowing user headers to take precedence.
    const headers = new Headers(options.headers);

    // Set default Content-Type if not already set by user
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    // Add Authorization header if token exists
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    } else {
      // If no token, ensure Authorization header is not sent with an empty 'Bearer ' string
      headers.delete('Authorization');
    }

    // Add ngrok header (always)
    headers.set("ngrok-skip-browser-warning", "true");

    const response = await fetch(url, {
      ...options, // Spread other fetch options first
      headers: headers, // Use our constructed Headers object
    });

    // 3. Improved Error Handling
    if (!response.ok) {
      let errorMessage = `API Error: ${response.status} ${response.statusText}`;
      let errorBody: unknown = null;

      const contentType = response.headers.get('content-type');

      // Attempt to parse JSON error response if content type is JSON
      if (contentType && contentType.includes('application/json')) {
        try {
          errorBody = await response.json();
          if (errorBody && typeof errorBody === 'object' && 'message' in errorBody) {
            errorMessage = errorBody.message as string;
          } else if (typeof errorBody === 'string') {
            errorMessage = errorBody;
          }
        } catch (e) {
          console.warn(`Failed to parse JSON error response for ${url} (status: ${response.status}):`, e);
        }
      } else {
        // If not JSON, try to get raw text error message
        try {
          const text = await response.text();
          if (text) {
            errorMessage = text;
          }
        } catch (e) {
          console.warn(`Failed to read text error response for ${url} (status: ${response.status}):`, e);
        }
      }

      // Throw a structured ApiError
      throw new ApiError(errorMessage, response.status);
    }

    // 4. Handle 204 No Content or non-JSON successful responses
    const contentType = response.headers.get('content-type');
    if (response.status === 204 || (contentType && !contentType.includes('application/json'))) {
      // For 204 No Content or non-JSON success, return undefined.
      // Callers expecting a specific type T should handle this case or use makeRequest<void>().
      return undefined as T;
    }

    return response.json();
  }
