import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Forgot Password - Virtual Showroom',
  description: 'Reset your Virtual Showroom password',
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordForm />;
}