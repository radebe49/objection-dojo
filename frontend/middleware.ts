import { authkitMiddleware } from '@workos-inc/authkit-nextjs';

// Use page-based auth - protected routes use ensureSignedIn option
export default authkitMiddleware();

// Match routes that need auth session management
export const config = {
  matcher: [
    '/',
    '/simulation/:path*',
    '/callback',
    '/login',
    '/api/auth/:path*',
  ],
};
