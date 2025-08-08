import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

import { AuthProvider } from '@/contexts/AuthContext'
import { TenantProvider } from '@/contexts/TenantContext'
import { Toaster } from 'react-hot-toast'
import { ReactQueryProvider } from '@/lib/react-query'

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "MEDINA Swimwear - Virtual Designer Showroom",
  description: "Premium swimwear collections with technical specifications and virtual showroom experience",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ReactQueryProvider>
          <AuthProvider>
            <TenantProvider>
              {children}
              <Toaster 
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#4ade80',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </TenantProvider>
          </AuthProvider>
        </ReactQueryProvider>
      </body>
    </html>
  )
}
