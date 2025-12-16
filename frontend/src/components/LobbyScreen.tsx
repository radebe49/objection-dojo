"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { AuthButton } from "./AuthButton";
import { Play, Target, Mic } from "lucide-react";

interface LobbyScreenProps {
  user?: {
    id: string;
    email: string;
    firstName: string | null;
    lastName: string | null;
  } | null;
  signInUrl?: string;
  signUpUrl?: string;
}

export default function LobbyScreen({ 
  user = null, 
  signInUrl = "/login",
  signUpUrl = "/signup"
}: LobbyScreenProps) {
  const router = useRouter();

  const handleStartSimulation = () => {
    // Pass user ID to simulation if logged in
    const params = user ? `?userId=${user.id}` : "";
    router.push(`/simulation${params}`);
  };

  return (
    <div className="min-h-screen min-h-[100dvh] flex flex-col bg-clean-white w-full">
      {/* Header with auth */}
      <header className="w-full px-4 py-3 flex justify-end">
        <AuthButton user={user} signInUrl={signInUrl} signUpUrl={signUpUrl} />
      </header>

      {/* Main content */}
      <main className="flex-1 flex flex-col items-center justify-center px-4">
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-4 sm:mb-6"
        >
          Dealfu
        </motion.h1>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="text-base sm:text-lg text-gray-600 text-center mb-8 sm:mb-12 max-w-md"
        >
          Master the art of the deal through AI-powered sales simulation
        </motion.p>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="flex flex-wrap justify-center gap-4 sm:gap-6 mb-8 sm:mb-12"
        >
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Target className="w-4 h-4 text-primary" />
            <span>Objection Handling</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <Mic className="w-4 h-4 text-primary" />
            <span>Voice Enabled</span>
          </div>
        </motion.div>

        {/* Start button */}
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleStartSimulation}
          className="flex items-center gap-3 px-8 py-4 bg-primary text-white font-semibold text-lg rounded-xl shadow-lg hover:shadow-xl transition-shadow"
        >
          <Play className="w-5 h-5" />
          Start Simulation
        </motion.button>

        {!user && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3, delay: 0.4 }}
            className="mt-4 text-sm text-gray-400"
          >
            Sign in to save your progress
          </motion.p>
        )}
      </main>

      {/* Footer */}
      <footer className="w-full px-4 py-4 text-center text-xs text-gray-400">
        Powered by Cerebras AI & ElevenLabs
      </footer>
    </div>
  );
}
