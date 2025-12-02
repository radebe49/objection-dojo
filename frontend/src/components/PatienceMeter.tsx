"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

interface PatienceMeterProps {
  value: number; // 0-100
}

/**
 * PatienceMeter component - Displays the AI persona's patience level.
 * 
 * Accessibility:
 * - Uses progressbar role with aria-valuenow, aria-valuemin, aria-valuemax
 * - aria-label provides context for screen readers
 * - Color changes are supplemented with text for color-blind users
 */
export default function PatienceMeter({ value }: PatienceMeterProps) {
  const prevValueRef = useRef(value);
  const [highlightColor, setHighlightColor] = useState<string | null>(null);

  // Clamp value to 0-100
  const clampedValue = Math.max(0, Math.min(100, value));

  useEffect(() => {
    const prevValue = prevValueRef.current;
    
    if (value > prevValue) {
      // Green highlight on increase
      setHighlightColor("#22c55e");
    } else if (value < prevValue) {
      // Red highlight on decrease
      setHighlightColor("#ef4444");
    }

    prevValueRef.current = value;

    // Reset highlight after animation
    const timer = setTimeout(() => {
      setHighlightColor(null);
    }, 300);

    return () => clearTimeout(timer);
  }, [value]);

  // Generate accessible label based on patience level
  const getStatusLabel = (): string => {
    if (clampedValue <= 20) return "Critical - prospect is very impatient";
    if (clampedValue <= 40) return "Low - prospect is losing interest";
    if (clampedValue <= 60) return "Moderate - prospect is neutral";
    if (clampedValue <= 80) return "Good - prospect is engaged";
    return "Excellent - prospect is very interested";
  };

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-2 gap-2">
        <span 
          id="patience-label"
          className="text-sm font-medium text-clean-gray-500 shrink-0"
        >
          Patience
        </span>
        <motion.span
          key={clampedValue}
          initial={{ scale: 1.2 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.3 }}
          className="text-sm font-bold text-primary tabular-nums"
          aria-hidden="true"
        >
          {clampedValue}%
        </motion.span>
      </div>
      <div 
        className="w-full h-3 sm:h-4 bg-clean-gray-200 rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={clampedValue}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-labelledby="patience-label"
        aria-label={`Patience meter at ${clampedValue}%. ${getStatusLabel()}`}
      >
        <motion.div
          className="h-full rounded-full"
          initial={false}
          animate={{
            width: `${clampedValue}%`,
            backgroundColor: highlightColor || "#0066CC",
          }}
          transition={{ duration: 0.3, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
