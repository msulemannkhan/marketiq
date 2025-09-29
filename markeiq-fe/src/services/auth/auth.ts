import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  RegisterResponse,
  User, 
  RefreshTokenRequest, 
  RefreshTokenResponse, 
  UpdateProfileRequest 
} from '@/types/auth';
import { makeRequest } from '@/services/utils';

const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  REMEMBER_ME: 'remember_me',
  LAST_ACTIVITY: 'last_activity'
} as const;

export class AuthService {

  static async login(credentials: LoginRequest): Promise<AuthResponse> {
    return makeRequest<AuthResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  }

  static async register(userData: RegisterRequest): Promise<RegisterResponse> {
    return makeRequest<RegisterResponse>('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  static async refreshToken(refreshTokenData: RefreshTokenRequest): Promise<RefreshTokenResponse> {
    return makeRequest<RefreshTokenResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      body: JSON.stringify(refreshTokenData),
    });
  }

  static async logout(): Promise<string> {
    const refreshToken = this.getRefreshToken();
    if (refreshToken) {
      try {
        await makeRequest<string>('/api/v1/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (error) {
        console.warn('Logout request failed:', error);
      }
    }
    this.clearAuthData();
    return 'Logged out successfully';
  }

  static async getCurrentUser(): Promise<User> {
    return makeRequest<User>('/api/v1/auth/me', {
      method: 'GET',
    });
  }

  static async updateProfile(profileData: UpdateProfileRequest): Promise<User> {
    return makeRequest<User>('/api/v1/auth/me', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  }

  static saveAuthData(authResponse: AuthResponse, rememberMe: boolean = false): void {
    if (typeof window !== 'undefined') {
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem(STORAGE_KEYS.AUTH_TOKEN, authResponse.access_token);
      storage.setItem(STORAGE_KEYS.REFRESH_TOKEN, authResponse.refresh_token);
      storage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(authResponse.user));
      storage.setItem(STORAGE_KEYS.REMEMBER_ME, rememberMe.toString());
      storage.setItem(STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
      
      // Set cookie for middleware (expires in 7 days for remembered, 1 day for not remembered)
      const expiresInDays = rememberMe ? 7 : 1;
      const expires = new Date();
      expires.setDate(expires.getDate() + expiresInDays);
      
      document.cookie = `auth_token=${authResponse.access_token}; expires=${expires.toUTCString()}; path=/; SameSite=Lax`;
    }
  }

  static convertRegisterResponseToUser(registerResponse: RegisterResponse): User {
    return {
      id: registerResponse.id,
      email: registerResponse.email,
      username: registerResponse.username,
      full_name: registerResponse.full_name,
      bio: '', // Default empty bio
      timezone: 'UTC', // Default timezone
      is_active: registerResponse.is_active,
      is_verified: registerResponse.is_verified,
      created_at: registerResponse.created_at,
      last_login_at: registerResponse.last_login_at,
      avatar_url: registerResponse.avatar_url,
      updated_at: registerResponse.created_at, // Use created_at as updated_at
    };
  }

  static saveRegisterData(registerResponse: RegisterResponse, rememberMe: boolean = false): void {
    if (typeof window !== 'undefined') {
      const user = this.convertRegisterResponseToUser(registerResponse);
      const storage = rememberMe ? localStorage : sessionStorage;
      
      // For register, we don't have tokens yet, so we'll store user data and mark as registered
      storage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
      storage.setItem(STORAGE_KEYS.REMEMBER_ME, rememberMe.toString());
      storage.setItem(STORAGE_KEYS.LAST_ACTIVITY, Date.now().toString());
      
      // Note: No auth token is set for register response, user needs to login
    }
  }

  static clearAuthData(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      localStorage.removeItem(STORAGE_KEYS.REMEMBER_ME);
      localStorage.removeItem(STORAGE_KEYS.LAST_ACTIVITY);
      sessionStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
      sessionStorage.removeItem(STORAGE_KEYS.USER_DATA);
      sessionStorage.removeItem(STORAGE_KEYS.REMEMBER_ME);
      sessionStorage.removeItem(STORAGE_KEYS.LAST_ACTIVITY);
      
      // Clear auth cookies more thoroughly
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Lax';
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict';
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=None; Secure';
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=' + window.location.hostname;
      document.cookie = 'auth_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=.' + window.location.hostname;
    }
  }

  static getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN) || sessionStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    }
    return null;
  }

  static getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN) || sessionStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    }
    return null;
  }

  static getUser(): User | null {
    if (typeof window !== 'undefined') {
      const userDataString = localStorage.getItem(STORAGE_KEYS.USER_DATA) || sessionStorage.getItem(STORAGE_KEYS.USER_DATA);
      
      if (userDataString) {
        try {
          // The error "undefined" is not valid JSON occurs when JSON.parse is called with the string "undefined".
          // This can happen if `JSON.stringify(undefined)` was stored, as localStorage converts `undefined` to the string "undefined".
          // JSON.parse("null") is valid and returns null, so no special handling is needed for the "null" string.
          if (userDataString === 'undefined') {
            return null;
          }
          return JSON.parse(userDataString);
        } catch (e) {
          console.error("Error parsing user data from storage:", e);
          // Clear potentially corrupted user data to prevent future errors
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
          sessionStorage.removeItem(STORAGE_KEYS.USER_DATA);
          return null;
        }
      }
    }
    return null;
  }

  static isRemembered(): boolean {
    if (typeof window !== 'undefined') {
      return localStorage.getItem(STORAGE_KEYS.REMEMBER_ME) === 'true';
    }
    return false;
  }

  static getLastActivity(): number | null {
    if (typeof window !== 'undefined') {
      const lastActivity = localStorage.getItem(STORAGE_KEYS.LAST_ACTIVITY) || sessionStorage.getItem(STORAGE_KEYS.LAST_ACTIVITY);
      return lastActivity ? parseInt(lastActivity, 10) : null;
    }
    return null;
  }

  static updateLastActivity(): void {
    if (typeof window !== 'undefined') {
      const timestamp = Date.now().toString();
      const storage = this.isRemembered() ? localStorage : sessionStorage;
      storage.setItem(STORAGE_KEYS.LAST_ACTIVITY, timestamp);
    }
  }

  static saveUserData(user: User): void {
    if (typeof window !== 'undefined') {
      const storage = this.isRemembered() ? localStorage : sessionStorage;
      storage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    }
  }

  static isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }

  static shouldRefreshToken(): boolean {
    const lastActivity = this.getLastActivity();
    if (!lastActivity) return false;
    
    const now = Date.now();
    const timeSinceLastActivity = now - lastActivity;
    
    // If user is remembered, refresh token is valid for 7 days
    // If not remembered, refresh token is valid for 2 days
    const maxInactiveTime = this.isRemembered() ? 7 * 24 * 60 * 60 * 1000 : 2 * 24 * 60 * 60 * 1000;
    
    return timeSinceLastActivity < maxInactiveTime;
  }
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}