import { LoginForm } from '@/components/auth/LoginForm';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In - Virtual Showroom',
  description: 'Sign in to your Virtual Showroom account',
};

export default function LoginPage() {
  return <LoginForm />;
}