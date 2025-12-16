"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function LobbyScreen() {
  const router = useRouter();

  const handleStartSimulation = () => {
    router.push("/simulation");
  };

  return (
    <div className="min-h-screen min-h-[100dvh] flex flex-col items-center justify-center bg-clean-white px-4 w-full max-w-full overflow-x-hidden">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="text-3xl sm:text-4xl md:text-5xl font-bold text-primary mb-4 sm:mb-6 text-center px-2"
      >
        Dealfu
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.05 }}
        className="text-clean-gray-500 text-center max-w-md mb-8 sm:mb-12 px-4 text-sm sm:text-base"
      >
        Practice handling sales objections with an AI-powered skeptical CTO. 
        Use your voice to pitch and respond to objections.
      </motion.p>

      <motion.button
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3, delay: 0.1 }}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleStartSimulation}
        className="min-h-[44px] min-w-[44px] px-6 sm:px-8 py-3 sm:py-4 bg-primary text-clean-white font-semibold text-base sm:text-lg rounded-lg shadow-md hover:bg-primary-600 active:bg-primary-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2"
        aria-label="Start Simulation"
      >
        Start Simulation
      </motion.button>
    </div>
  );
}
