"use client";

import { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import ActionButton, { ActionButtonState } from "./ActionButton";
import PatienceMeter from "./PatienceMeter";
import GameOverScreen from "./GameOverScreen";
import { useToast } from "./ToastProvider";

// Lazy load WinScreen with confetti animation to reduce initial bundle size
const WinScreen = dynamic(() => import("./WinScreen"), {
  loading: () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 text-center">
        <p className="text-green-500 font-bold">Loading celebration...</p>
      </div>
    </div>
  ),
  ssr: false,
});
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { useAudioPlayer } from "@/hooks/useAudioPlayer";

interface Message {
  role: "user" | "ai";
  text: string;
  timestamp: number;
}

interface ChatResponse {
  ai_text: string;
  patience_score: number;
  deal_closed: boolean;
  audio_base64: string;
}

type GameStatus = "playing" | "won" | "lost";

/**
 * SimulationScreen component - Main game screen for Objection Dojo.
 *
 * **Feature: objection-dojo, Requirements 1.3, 1.4, 9.1**
 * - Generates session_id on mount using crypto.randomUUID()
 * - Initializes patience at 50%
 * - Requests microphone permission
 * - Composes ActionButton, PatienceMeter, conversation display
 */
export default function SimulationScreen() {
  // Session state - generated once on mount
  const [sessionId] = useState<string>(() => crypto.randomUUID());
  const [patienceScore, setPatienceScore] = useState<number>(50);
  const [gameStatus, setGameStatus] = useState<GameStatus>("playing");
  const [conversationHistory, setConversationHistory] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Hooks
  const { showToast } = useToast();
  const { start, stop, transcript, isListening, isSupported, error: speechError } = useSpeechRecognition();


  // Audio player with onEnded callback to re-enable button
  const handleAudioEnded = useCallback(() => {
    // Audio finished, button will be re-enabled via isPlaying state
  }, []);

  const { play: playAudio, isPlaying } = useAudioPlayer({
    onEnded: handleAudioEnded,
  });

  // Derive button state from current conditions
  const buttonState: ActionButtonState = (() => {
    if (isPlaying || isLoading || gameStatus !== "playing") {
      return "disabled";
    }
    if (isListening) {
      return "recording";
    }
    return "idle";
  })();

  // Request microphone permission on mount (Requirement 1.4)
  useEffect(() => {
    const requestMicPermission = async () => {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
      } catch (err) {
        console.error("Microphone permission denied:", err);
        showToast("Microphone access is required for this simulation.", "error");
      }
    };

    requestMicPermission();
  }, [showToast]);

  // Show error if Web Speech API is not supported (Requirement 2.8)
  useEffect(() => {
    if (!isSupported && speechError) {
      showToast(speechError, "error");
    }
  }, [isSupported, speechError, showToast]);

  // Check win/loss conditions when patience changes
  useEffect(() => {
    if (gameStatus !== "playing") return;

    if (patienceScore <= 0) {
      setGameStatus("lost");
    } else if (patienceScore >= 100) {
      setGameStatus("won");
    }
  }, [patienceScore, gameStatus]);

  /**
   * Validates that transcript contains non-whitespace content.
   * Property 1: Whitespace Input Rejection
   */
  const isValidTranscript = (text: string): boolean => {
    return text.trim().length > 0;
  };


  /**
   * Sends user message to backend API and processes response.
   * Requirements: 2.6, 3.5, 4.1, 7.1, 7.2, 7.4
   */
  const sendMessage = async (userText: string) => {
    // Store current patience for error recovery (Property 8: Error Preserves Patience)
    const patienceBeforeRequest = patienceScore;

    setIsLoading(true);

    // Add user message to conversation
    const userMessage: Message = {
      role: "user",
      text: userText,
      timestamp: Date.now(),
    };
    setConversationHistory((prev) => [...prev, userMessage]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_text: userText,
          current_patience: patienceBeforeRequest,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      // Add AI response to conversation
      const aiMessage: Message = {
        role: "ai",
        text: data.ai_text,
        timestamp: Date.now(),
      };
      setConversationHistory((prev) => [...prev, aiMessage]);

      // Update patience score (Requirement 4.1)
      setPatienceScore(data.patience_score);

      // Check for deal closed win condition (Requirement 5.3)
      if (data.deal_closed) {
        setGameStatus("won");
      }

      // Play audio response (Requirement 3.6)
      if (data.audio_base64) {
        playAudio(data.audio_base64);
      }
    } catch (err) {
      console.error("Chat API error:", err);
      // Show error toast (Requirement 7.1)
      showToast("Connection unstable. Say that again?", "error");
      // Do NOT deduct patience on error (Requirement 7.2, Property 8)
      // Patience remains at patienceBeforeRequest (already set)
    } finally {
      setIsLoading(false);
    }
  };


  /**
   * Handles ActionButton click - toggles recording state.
   * Requirements: 2.2, 2.3, 2.4, 2.5, 2.6
   */
  const handleActionButtonClick = () => {
    if (isListening) {
      // Stop recording and process transcript
      stop();

      // Validate transcript (Requirement 2.4, Property 1: Whitespace Input Rejection)
      if (!isValidTranscript(transcript)) {
        // Show toast for empty input (Requirement 2.5)
        showToast("I didn't hear anything.", "info");
        // Reset without API call (Requirement 2.4)
        return;
      }

      // Valid text - send to API (Requirement 2.6, Property 2: Valid Text Triggers API Call)
      sendMessage(transcript);
    } else {
      // Start recording (Requirement 2.2)
      start();
    }
  };

  return (
    <div className="min-h-screen min-h-[100dvh] flex flex-col bg-clean-white w-full max-w-full overflow-x-hidden">
      {/* Header with Patience Meter - banner landmark */}
      <header 
        className="p-3 sm:p-4 border-b border-clean-gray-200 shrink-0"
        role="banner"
      >
        <div className="max-w-md mx-auto px-1">
          <h1 className="text-lg sm:text-xl font-bold text-primary mb-3 sm:mb-4 text-center">
            Objection Dojo
          </h1>
          <PatienceMeter value={patienceScore} />
        </div>
      </header>

      {/* Conversation Display - main content area */}
      <main 
        className="flex-1 overflow-y-auto p-3 sm:p-4"
        role="main"
        aria-label="Conversation history"
      >
        <div className="max-w-md mx-auto space-y-3 sm:space-y-4">
          {conversationHistory.length === 0 && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center text-clean-gray-400 py-6 sm:py-8 text-sm sm:text-base px-4"
            >
              Tap the microphone to start your pitch
            </motion.p>
          )}
          
          {/* Conversation messages with proper ARIA roles */}
          <div 
            role="log" 
            aria-live="polite" 
            aria-label="Sales conversation"
          >
            {conversationHistory.map((message, index) => (
              <motion.div
                key={`${message.timestamp}-${index}`}
                initial={{ opacity: 0, y: 15, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ 
                  duration: 0.25,
                  ease: [0.25, 0.46, 0.45, 0.94]
                }}
                className={`p-3 rounded-lg break-words shadow-sm mb-3 sm:mb-4 ${
                  message.role === "user"
                    ? "bg-primary text-clean-white ml-4 sm:ml-8"
                    : "bg-clean-gray-100 text-clean-gray-700 mr-4 sm:mr-8"
                }`}
                role="article"
                aria-label={message.role === "user" ? "Your message" : "AI response"}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>
              </motion.div>
            ))}
          </div>

          {/* Loading indicator with spinner */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col items-center justify-center py-6 gap-3"
              role="status"
              aria-label="Processing your message"
            >
              {/* Spinner */}
              <motion.div
                className="w-8 h-8 border-3 border-clean-gray-200 border-t-primary rounded-full"
                animate={{ rotate: 360 }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  ease: "linear",
                }}
                style={{ borderWidth: "3px" }}
                aria-hidden="true"
              />
              {/* Bouncing dots */}
              <div className="flex space-x-1" aria-hidden="true">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-primary rounded-full"
                    animate={{ y: [0, -6, 0] }}
                    transition={{
                      duration: 0.5,
                      repeat: Infinity,
                      delay: i * 0.1,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </div>
              <p className="text-xs text-clean-gray-400">Processing your pitch...</p>
            </motion.div>
          )}

          {/* Live transcript while recording */}
          {isListening && transcript && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-3 rounded-lg bg-primary/10 border border-primary/20 ml-4 sm:ml-8 break-words"
              role="status"
              aria-live="polite"
              aria-label="Live transcription"
            >
              <p className="text-sm text-primary italic">{transcript}...</p>
            </motion.div>
          )}
        </div>
      </main>

      {/* Action Button Footer - contentinfo landmark */}
      <footer 
        className="p-4 sm:p-6 border-t border-clean-gray-200 shrink-0 safe-area-inset-bottom"
        role="contentinfo"
      >
        <div className="flex justify-center">
          <ActionButton 
            state={buttonState} 
            onClick={handleActionButtonClick}
            isLoading={isLoading}
          />
        </div>
        {isListening && (
          <motion.p 
            initial={{ opacity: 0, y: 5 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center text-xs sm:text-sm text-clean-gray-500 mt-2"
            role="status"
            aria-live="polite"
          >
            Listening... Tap to send
          </motion.p>
        )}
      </footer>

      {/* Game Over Screen - Requirements 5.1, 5.4 */}
      {gameStatus === "lost" && <GameOverScreen />}

      {/* Win Screen - Requirements 5.2, 5.3, 5.5 */}
      {gameStatus === "won" && <WinScreen />}
    </div>
  );
}
