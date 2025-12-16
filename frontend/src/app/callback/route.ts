import { handleAuth } from '@workos-inc/authkit-nextjs';

// Handle the OAuth callback from WorkOS
// Redirects to '/' after successful authentication
export const GET = handleAuth();
