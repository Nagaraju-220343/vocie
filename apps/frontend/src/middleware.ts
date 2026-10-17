import { NextRequest, NextResponse } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // If visiting /demo-login, redirect directly to /dashboard
  if (pathname === '/demo-login') {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Allow direct access to the dashboard and all pages
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
