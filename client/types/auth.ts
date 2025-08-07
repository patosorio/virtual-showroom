import { User as FirebaseUser } from 'firebase/auth';

export interface User {
    id: string;
    email: string;
    firebase_uid: string;
    role: 'admin' | 'user' | 'viewer';
    is_active: boolean;
    display_name: string | null;
    photo_url: string | null;
    phone_number: string | null;
    last_login: string | null;
    login_count: number;
    created_at: string;
    updated_at: string;
  }
  
  export interface UserProfile {
    id: string;
    email: string;
    display_name: string | null;
    photo_url: string | null;
    phone_number: string | null;
    role: string;
    is_active: boolean;
    last_login: string | null;
    preferences: Record<string, any>;
  }
  
  export interface LoginRequest {
    id_token: string;
  }
  
  export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
    user: User;
  }
  
  export interface AuthState {
    user: User | null;
    firebaseUser: FirebaseUser | null;
    isLoading: boolean;
    isAuthenticated: boolean;
  }