"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect } from "react";
import { X } from "lucide-react";

export type ToastType = "info" | "error";

interface ToastProps {
  message: string;
  type?: ToastType;
  isVisible: boolean;
  onDismiss: () => void;
  autoDismissMs?: number;
}

export default function Toast({
  message,
  type = "info",
  isVisible,
  onDismiss,
  autoDismissMs = 3000,
}: ToastProps) {
  useEffect(() => {
    if (isVisible && autoDismissMs > 0) {
      const timer = setTimeout(() => {
        onDismiss();
      }, autoDismissMs);

      return () => clearTimeout(timer);
    }
  }, [isVisible, autoDismissMs, onDismiss]);

  const bgColor = type === "error" ? "bg-red-500" : "bg-primary";
  const borderColor = type === "error" ? "border-red-600" : "border-primary-600";

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className={`fixed top-4 left-4 right-4 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 z-50 ${bgColor} ${borderColor} border text-clean-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3 max-w-sm mx-auto sm:mx-0`}
          role="alert"
          aria-live="polite"
        >
          <span className="text-sm font-medium flex-1">{message}</span>
          <button
            onClick={onDismiss}
            className="min-h-[44px] min-w-[44px] p-2 hover:bg-white/20 active:bg-white/30 rounded transition-colors flex items-center justify-center shrink-0"
            aria-label="Dismiss notification"
          >
            <X size={16} />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
