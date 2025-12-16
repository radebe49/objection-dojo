"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

interface WinScreenProps {
  onPlayAgain?: () => void;
}

interface ConfettiPiece {
  id: number;
  color: string;
  left: string;
  delay: number;
  duration: number;
  rotation: number;
}

/**
 * WinScreen component - Displays when the user wins the simulation.
 *
 * **Feature: dealfu, Requirements 5.2, 5.3, 5.5**
 * - Displays "Sale Closed" message when patience reaches 100% or deal_closed is true
 * - Shows confetti animation for celebration
 * - Shows "Play Again" button linking to Lobby
 */
export default function WinScreen({ onPlayAgain }: WinScreenProps) {
  const router = useRouter();
  const [confetti, setConfetti] = useState<ConfettiPiece[]>([]);
  const [windowHeight, setWindowHeight] = useState(800);

  // Generate confetti pieces on mount
  useEffect(() => {
    // Set window height for animation
    setWindowHeight(window.innerHeight);

    const colors = ["#0066CC", "#22c55e", "#eab308", "#ef4444", "#8b5cf6"];
    const pieces: ConfettiPiece[] = Array.from({ length: 50 }).map((_, i) => ({
      id: i,
      color: colors[i % colors.length],
      left: `${Math.random() * 100}%`,
      delay: Math.random() * 0.5,
      duration: 2 + Math.random() * 2,
      rotation: Math.random() * 360,
    }));
    setConfetti(pieces);
  }, []);

  const handlePlayAgain = () => {
    if (onPlayAgain) {
      onPlayAgain();
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
      aria-labelledby="win-title"
      aria-describedby="win-description"
    >
      {/* Confetti animation */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {confetti.map((piece) => (
          <motion.div
            key={piece.id}
            className="absolute w-2 sm:w-3 h-2 sm:h-3 rounded-full"
            style={{
              backgroundColor: piece.color,
              left: piece.left,
            }}
            initial={{ y: -20, opacity: 1 }}
            animate={{
              y: windowHeight + 20,
              opacity: 0,
              rotate: piece.rotation,
            }}
            transition={{
              duration: piece.duration,
              delay: piece.delay,
              ease: "easeOut",
            }}
          />
        ))}
      </div>

      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="bg-clean-white rounded-xl p-6 sm:p-8 text-center shadow-xl relative z-10 max-w-sm w-full"
      >
        <h2
          id="win-title"
          className="text-xl sm:text-2xl font-bold text-green-500 mb-3 sm:mb-4"
        >
          Sale Closed!
        </h2>
        <p
          id="win-description"
          className="text-sm sm:text-base text-clean-gray-500 mb-5 sm:mb-6"
        >
          Congratulations! You convinced the Skeptic CTO.
        </p>
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handlePlayAgain}
          className="min-h-[44px] min-w-[44px] px-6 py-3 bg-primary text-clean-white font-semibold rounded-lg hover:bg-primary-600 active:bg-primary-700 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary-300 focus:ring-offset-2"
          aria-label="Play Again - Return to Lobby"
        >
          Play Again
        </motion.button>
      </motion.div>
    </motion.div>
  );
}
