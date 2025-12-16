import { withAuth } from "@workos-inc/authkit-nextjs";
import LobbyScreen from "@/components/LobbyScreen";

export default async function Home() {
  // Get user from WorkOS session (null if not signed in)
  let user = null;
  
  try {
    const auth = await withAuth();
    user = auth.user;
  } catch (error) {
    // Auth middleware not configured or credentials invalid - continue without auth
    console.warn('Auth not available:', error);
  }

  return (
    <LobbyScreen
      user={user ? {
        id: user.id,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
      } : null}
    />
  );
}
