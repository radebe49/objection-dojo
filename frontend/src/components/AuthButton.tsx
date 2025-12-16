"use client";

import { motion } from "framer-motion";
import { LogIn, LogOut, User } from "lucide-react";

interface AuthButtonProps {
  user?: {
    id: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
  } | null;
  signInUrl?: string;
  signUpUrl?: string;
}

export function AuthButton({
  user,
  signInUrl = "/login",
  signUpUrl = "/signup",
}: AuthButtonProps) {
  if (user) {
    return (
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <User className="w-4 h-4" />
          <span className="hidden sm:inline">
            {user.firstName || user.email}
          </span>
        </div>
        <motion.a
          href="/api/auth/signout"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          <LogOut className="w-4 h-4" />
          <span className="hidden sm:inline">Sign out</span>
        </motion.a>
      </div>
    );
  }

  return (
    <motion.a
      href={signInUrl}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
    >
      <LogIn className="w-4 h-4" />
      Sign in
    </motion.a>
  );
}
