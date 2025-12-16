"use client";

import { useState, useCallback, useRef, useEffect } from "react";

// Type definitions for Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((event: SpeechRecognitionEvent) => void) | null;
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null;
  onend: (() => void) | null;
  onstart: (() => void) | null;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

interface UseSpeechRecognitionReturn {
  start: () => void;
  stop: () => void;
  transcript: string;
  isListening: boolean;
  isSupported: boolean;
  error: string | null;
}

/**
 * Custom hook wrapping the Web Speech API for speech-to-text functionality.
 *
 * **Feature: dealfu, Requirements 2.7, 2.8**
 * - Exposes start(), stop(), transcript, isListening
 * - Handles browser compatibility check
 * - Auto-restarts recognition when it ends unexpectedly (silence detection)
 */
export function useSpeechRecognition(): UseSpeechRecognitionReturn {
  const [transcript, setTranscript] = useState<string>("");
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const recognitionRef = useRef<SpeechRecognition | null>(null);
  // Track if we intentionally want to be listening (vs browser auto-stopping)
  const shouldBeListeningRef = useRef<boolean>(false);
  // Store accumulated final transcript across restarts
  const finalTranscriptRef = useRef<string>("");
  // Track current interim transcript (resets on each result)
  const interimTranscriptRef = useRef<string>("");

  // Check browser support on mount
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setIsSupported(false);
      // Detect Brave browser
      const isBrave =
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (navigator as any).brave !== undefined ||
        navigator.userAgent.includes("Brave");
      if (isBrave) {
        setError(
          "Brave blocks speech recognition by default. Enable it in brave://settings/privacy or use Chrome."
        );
      } else {
        setError(
          "Speech recognition not supported. Please use Chrome or Edge browser."
        );
      }
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let currentInterim = "";

      // Process all results from the beginning to build complete picture
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;

        if (result.isFinal) {
          // Only add new final results (check if this is a new final result)
          if (i >= event.resultIndex) {
            finalTranscriptRef.current += text + " ";
          }
        } else {
          // Interim results - just capture the latest
          currentInterim = text;
        }
      }

      interimTranscriptRef.current = currentInterim;

      // Update state with final + current interim
      const fullTranscript =
        finalTranscriptRef.current + interimTranscriptRef.current;
      setTranscript(fullTranscript.trim());
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      // Ignore "no-speech" and "aborted" errors - these are expected during restarts
      if (event.error === "no-speech" || event.error === "aborted") {
        // Still try to restart if we should be listening
        return;
      }
      console.error("Speech recognition error:", event.error);
      setError(`Speech recognition error: ${event.error}`);
      shouldBeListeningRef.current = false;
      setIsListening(false);
    };

    recognition.onend = () => {
      // If we should still be listening, restart recognition after a brief delay
      // This handles the browser auto-stopping due to silence
      if (shouldBeListeningRef.current) {
        // Small delay to prevent rapid restart loops
        setTimeout(() => {
          if (shouldBeListeningRef.current && recognitionRef.current) {
            try {
              recognitionRef.current.start();
            } catch (err) {
              // If restart fails, update state
              console.error("Failed to restart speech recognition:", err);
              shouldBeListeningRef.current = false;
              setIsListening(false);
            }
          }
        }, 100);
      } else {
        setIsListening(false);
      }
    };

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognitionRef.current = recognition;

    return () => {
      shouldBeListeningRef.current = false;
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const start = useCallback(() => {
    if (!recognitionRef.current || !isSupported) {
      return;
    }

    // Reset all transcript state
    finalTranscriptRef.current = "";
    interimTranscriptRef.current = "";
    setTranscript("");
    setError(null);
    shouldBeListeningRef.current = true;

    try {
      recognitionRef.current.start();
    } catch (err) {
      // Handle case where recognition is already started
      console.error("Failed to start speech recognition:", err);
      shouldBeListeningRef.current = false;
    }
  }, [isSupported]);

  const stop = useCallback(() => {
    // Mark that we intentionally want to stop
    shouldBeListeningRef.current = false;

    if (!recognitionRef.current) {
      return;
    }

    try {
      recognitionRef.current.stop();
    } catch (err) {
      console.error("Failed to stop speech recognition:", err);
    }
  }, []);

  return {
    start,
    stop,
    transcript,
    isListening,
    isSupported,
    error,
  };
}

export default useSpeechRecognition;
