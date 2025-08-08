import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Define protected routes
const protectedRoutes = [
  '/',
  '/collections',
  '/products', 
  '/settings',
  '/admin'
]

// Define auth routes (should redirect if authenticated)
const authRoutes = [
  '/login',
  '/register', 
  '/forgot-password'
]

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if current path is protected
  const isProtectedRoute = protectedRoutes.some(route => 
    pathname === route || pathname.startsWith(`${route}/`)
  )

  // Check if current path is an auth route
  const isAuthRoute = authRoutes.includes(pathname)

  // For protected routes, we'll handle auth check on client side
  // This middleware just ensures proper routing structure

  // Redirect root auth routes to login if not authenticated
  if (pathname === '/') {
    // Let the client-side auth handling take care of redirects
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}