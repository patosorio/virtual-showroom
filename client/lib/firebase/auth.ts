import {
    signInWithEmailAndPassword,
    createUserWithEmailAndPassword,
    signInWithPopup,
    GoogleAuthProvider,
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
  
  // Initialize Google Auth Provider
  const googleProvider = new GoogleAuthProvider();
  
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
  
    // Sign in with Google
    signInWithGoogle: async () => {
      try {
        // Configure Google provider for better UX
        googleProvider.setCustomParameters({
          prompt: 'select_account'
        });
        
        const result = await signInWithPopup(auth, googleProvider);
        return result.user;
      } catch (error: any) {
        // Handle specific Google auth errors
        if (error.code === 'auth/popup-closed-by-user') {
          throw new Error('Sign-in cancelled');
        } else if (error.code === 'auth/popup-blocked') {
          throw new Error('Popup blocked by browser. Please allow popups and try again.');
        } else if (error.code === 'auth/account-exists-with-different-credential') {
          throw new Error('An account already exists with the same email address but different sign-in credentials.');
        }
        throw error;
      }
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