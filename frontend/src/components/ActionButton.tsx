"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Mic, Square } from "lucide-react";
import { useEffect, useRef, useCallback } from "react";
import { useIsMobile } from "@/hooks/useIsMobile";

export type ActionButtonState = "idle" | "recording" | "disabled";

interface ActionButtonProps {
  state: ActionButtonState;
  onClick: () => void;
  /** Callback when recording starts (for mobile press-and-hold) */
  onRecordStart?: () => void;
  /** Callback when recording stops (for mobile press-and-hold) */
  onRecordStop?: () => void;
  /** Optional: show loading spinner when processing */
  isLoading?: boolean;
}

/**
 * ActionButton component with state machine for Click-to-Talk functionality.
 * 
 * **Feature: dealfu, Requirements 2.1, 2.2, 2.3, 6.1**
 * - Idle state: Mic icon, blue background
 * - Recording state: Stop icon, pulsing animation
 * - Disabled state: greyed out, non-interactive
 * 
 * Interaction modes:
 * - Desktop: Click to start recording, click again to stop and send
 * - Mobile: Press and hold to record, release to send (WhatsApp-style)
 * 
 * Accessibility:
 * - Touch target: 80x80px (exceeds 44x44px WCAG minimum)
 * - ARIA labels describe current state and available action
 * - Focus ring visible for keyboard navigation (WCAG 2.4.7)
 * - Color contrast: White (#FFFFFF) on Primary Blue (#0066CC) = 4.5:1 ratio (WCAG AA)
 */
export default function ActionButton({ 
  state, 
  onClick, 
  onRecordStart,
  onRecordStop,
  isLoading = false 
}: ActionButtonProps) {
  const isDisabled = state === "disabled";
  const isRecording = state === "recording";
  const isMobile = useIsMobile();
  const isPressingRef = useRef(false);
  const longPressTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Desktop: simple click toggle
  const handleClick = () => {
    if (isDisabled || isMobile) return;
    onClick();
  };

  // Mobile: press and hold handlers
  const handlePressStart = useCallback(() => {
    if (isDisabled || !isMobile) return;
    
    isPressingRef.current = true;
    
    // Small delay to distinguish from tap (prevents accidental triggers)
    longPressTimerRef.current = setTimeout(() => {
      if (isPressingRef.current && onRecordStart) {
        onRecordStart();
      }
    }, 100);
  }, [isDisabled, isMobile, onRecordStart]);

  const handlePressEnd = useCallback(() => {
    if (!isMobile) return;
    
    isPressingRef.current = false;
    
    if (longPressTimerRef.current) {
      clearTimeout(longPressTimerRef.current);
      longPressTimerRef.current = null;
    }
    
    // Only trigger stop if we were recording
    if (isRecording && onRecordStop) {
      onRecordStop();
    }
  }, [isMobile, isRecording, onRecordStop]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (longPressTimerRef.current) {
        clearTimeout(longPressTimerRef.current);
      }
    };
  }, []);

  // Generate descriptive ARIA label based on current state and device
  const getAriaLabel = (): string => {
    if (isLoading && isDisabled) {
      return "Processing your message, please wait";
    }
    if (isDisabled) {
      return "Microphone button disabled, waiting for audio to finish";
    }
    if (isRecording) {
      return isMobile 
        ? "Recording in progress. Release to send your message"
        : "Recording in progress. Click to stop recording and send your message";
    }
    return isMobile
      ? "Press and hold to record your sales pitch"
      : "Click to start recording your sales pitch";
  };

  // Base styles for the button - 80x80px touch target (exceeds 44x44px minimum)
  const baseStyles = `
    relative flex items-center justify-center
    w-20 h-20 rounded-full
    transition-all duration-200
    focus:outline-none focus-visible:ring-4 focus-visible:ring-primary-300 focus-visible:ring-offset-2 focus-visible:ring-offset-white
    touch-action-manipulation
    select-none
    -webkit-tap-highlight-color-transparent
  `;

  // State-specific styles
  const stateStyles = {
    idle: "bg-primary hover:bg-primary-600 active:bg-primary-700 cursor-pointer shadow-lg hover:shadow-xl",
    recording: "bg-primary cursor-pointer shadow-lg",
    disabled: "bg-clean-gray-300 cursor-not-allowed opacity-60 shadow-md",
  };

  // Icon color based on state - White on blue meets WCAG AA contrast (4.5:1)
  const iconColor = isDisabled ? "#9CA3AF" : "#FFFFFF";

  return (
    <motion.button
      type="button"
      onClick={handleClick}
      // Mobile press-and-hold handlers
      onTouchStart={handlePressStart}
      onTouchEnd={handlePressEnd}
      onTouchCancel={handlePressEnd}
      // Mouse fallback for testing mobile behavior
      onMouseDown={isMobile ? handlePressStart : undefined}
      onMouseUp={isMobile ? handlePressEnd : undefined}
      onMouseLeave={isMobile && isRecording ? handlePressEnd : undefined}
      disabled={isDisabled}
      className={`${baseStyles} ${stateStyles[state]}`}
      whileHover={isDisabled ? {} : { scale: 1.05 }}
      whileTap={isDisabled ? {} : { scale: 0.92 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      aria-label={getAriaLabel()}
      aria-disabled={isDisabled}
      aria-busy={isLoading}
      aria-live="polite"
      role="button"
    >
      {/* Pulsing ring animation for recording state */}
      {isRecording && (
        <motion.div
          className="absolute inset-0 rounded-full bg-primary"
          initial={{ scale: 1, opacity: 0.5 }}
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.5, 0, 0.5],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      )}

      {/* Subtle press feedback ring */}
      <motion.div
        className="absolute inset-0 rounded-full border-2 border-white/30"
        initial={{ scale: 1, opacity: 0 }}
        whileTap={{ scale: 0.95, opacity: 1 }}
        transition={{ duration: 0.1 }}
      />

      {/* Icon with smooth transitions */}
      <AnimatePresence mode="wait">
        <motion.div
          className="relative z-10"
          key={isLoading ? "loading" : state}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          {isLoading && isDisabled ? (
            // Loading spinner when processing
            <motion.div
              className="w-8 h-8 border-3 border-gray-400 border-t-white rounded-full"
              animate={{ rotate: 360 }}
              transition={{
                duration: 1,
                repeat: Infinity,
                ease: "linear",
              }}
              style={{ borderWidth: "3px" }}
            />
          ) : isRecording ? (
            <Square size={32} color={iconColor} fill={iconColor} />
          ) : (
            <Mic size={32} color={iconColor} />
          )}
        </motion.div>
      </AnimatePresence>
    </motion.button>
  );
}
