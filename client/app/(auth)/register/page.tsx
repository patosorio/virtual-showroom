import { RegisterForm } from '@/components/auth/RegisterForm';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign Up - Virtual Showroom',
  description: 'Create your Virtual Showroom account',
};

export default function RegisterPage() {
  return <RegisterForm />;
}
