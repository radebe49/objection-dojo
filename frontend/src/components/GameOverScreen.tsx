"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

interface GameOverScreenProps {
  onRetry?: () => void;
}

/**
 * GameOverScreen component - Displays when the user loses the simulation.
 *
 * **Feature: dealfu, Requirements 5.1, 5.4**
 * - Displays "Call Failed" message when patience reaches 0%
 * - Shows "Try Again" button linking to Lobby
 */
export default function GameOverScreen({ onRetry }: GameOverScreenProps) {
  const router = useRouter();

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    } else {
      router.push("/");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-labelledby="game-over-title"
      aria-describedby="game-over-description"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="bg-clean-white rounded-xl p-6 sm:p-8 text-center shadow-xl max-w-sm w-full"
      >
        <h2
          id="game-over-title"
          className="text-xl sm:text-2xl font-bold text-red-500 mb-3 sm:mb-4"
        >
          Call Failed
        </h2>
        <p
          id="game-over-description"
          className="text-sm sm:text-base text-clean-gray-500 mb-5 sm:mb-6"
        >
          The prospect hung up. Better luck next time!
        </p>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleRetry}
          className="min-h-[44px] min-w-[44px] px-6 py-3 bg-primary text-clean-white font-semibold rounded-lg hover:bg-primary-600 active:bg-primary-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2"
          aria-label="Try Again - Return to Lobby"
        >
          Try Again
        </motion.button>
      </motion.div>
    </motion.div>
  );
}
