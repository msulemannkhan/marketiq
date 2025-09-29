export interface LoginRequest {
  login: string; // Can be username or email
  password: string;
  remember_me: boolean;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface RegisterResponse {
  email: string;
  username: string;
  full_name: string;
  id: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at: string;
  avatar_url: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  bio: string;
  timezone: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login_at: string;
  avatar_url: string | null;
  updated_at?: string;
  email_verified_at?: string;
  preferences?: Record<string, unknown>;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LogoutRequest {
  refresh_token: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  bio?: string;
  timezone?: string;
  avatar_url?: string;
}

export interface ApiError {
  message: string;
  status: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
}

export interface LoginFormData {
  login: string; // Can be username or email
  password: string;
  remember_me: boolean;
}

export interface RegisterFormData {
  full_name: string;
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  acceptTerms: boolean;
}