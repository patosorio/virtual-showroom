import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signOut,
    sendPasswordResetEmail,
    User as FirebaseUser,
  } from 'firebase/auth';
  import { auth } from './config';
  
  export interface AuthUser {
    uid: string;
    email: string | null;
    displayName: string | null;
    photoURL: string | null;
  }
  
  export const firebaseAuth = {
    // Sign in with email and password
    signIn: async (email: string, password: string) => {
      const result = await signInWithEmailAndPassword(auth, email, password);
      return result.user;
    },
  
    // Create account with email and password
    signUp: async (email: string, password: string, displayName?: string) => {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      return result.user;
    },
  
    // Sign out
    signOut: async () => {
      await signOut(auth);
    },
  
    // Send password reset email
    resetPassword: async (email: string) => {
      await sendPasswordResetEmail(auth, email);
    },
  
    // Get current user
    getCurrentUser: (): FirebaseUser | null => {
      return auth.currentUser;
    },
  
    // Get ID token for API requests
    getIdToken: async (): Promise<string | null> => {
      const user = auth.currentUser;
      if (user) {
        return await user.getIdToken();
      }
      return null;
    },
  };