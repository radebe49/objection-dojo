"use client";

import { useState, useCallback, useRef, useEffect } from "react";

interface UseVADOptions {
  /** Silence duration (ms) before auto-stopping. Default: 800ms (optimized for natural conversation) */
  silenceThreshold?: number;
  /** Minimum audio level to consider as speech (0-1). Default: 0.015 */
  speechThreshold?: number;
  /** How often to check audio levels (ms). Default: 50ms (faster detection) */
  checkInterval?: number;
  /** Callback when speech ends and transcript is ready */
  onSpeechEnd?: (transcript: string) => void;
  /** Callback when speech starts */
  onSpeechStart?: () => void;
  /** Whether VAD is enabled (can be disabled during AI playback) */
  enabled?: boolean;
}

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

interface UseVADReturn {
  /** Start listening with VAD */
  startListening: () => void;
  /** Stop listening completely */
  stopListening: () => void;
  /** Current transcript (interim + final) */
  transcript: string;
  /** Whether actively listening for speech */
  isListening: boolean;
  /** Whether currently detecting speech */
  isSpeaking: boolean;
  /** Whether browser supports speech recognition */
  isSupported: boolean;
  /** Any error message */
  error: string | null;
}

/**
 * Voice Activity Detection hook - automatically detects speech start/end.
 * Uses Web Speech API for transcription + AudioContext for VAD.
 */
export function useVoiceActivityDetection(
  options: UseVADOptions = {}
): UseVADReturn {
  const {
    // Optimized defaults for natural conversation flow
    silenceThreshold = 800,   // 0.8s - faster response, more natural
    speechThreshold = 0.015,  // Slightly higher to avoid false positives
    checkInterval = 50,       // 50ms - faster VAD detection
    onSpeechEnd,
    onSpeechStart,
    enabled = true,
  } = options;

  const [transcript, setTranscript] = useState<string>("");
  const [isListening, setIsListening] = useState<boolean>(false);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isSupported, setIsSupported] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Refs for audio analysis
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const checkIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Refs for speech recognition
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const finalTranscriptRef = useRef<string>("");
  const interimTranscriptRef = useRef<string>("");

  // Refs for VAD state
  const lastSpeechTimeRef = useRef<number>(0);
  const isSpeakingRef = useRef<boolean>(false);
  const hasSpokenRef = useRef<boolean>(false);
  const enabledRef = useRef<boolean>(enabled);

  // Keep enabled ref in sync and clear transcript when disabled
  useEffect(() => {
    enabledRef.current = enabled;
    
    // When VAD is disabled (AI speaking), clear any partial transcript
    // This prevents the AI's voice from being transcribed and sent as user input
    if (!enabled) {
      finalTranscriptRef.current = "";
      interimTranscriptRef.current = "";
      setTranscript("");
    }
  }, [enabled]);

  // Initialize speech recognition
  useEffect(() => {
    const SpeechRecognitionAPI =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionAPI) {
      setIsSupported(false);
      const isBrave =
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        (navigator as any).brave !== undefined ||
        navigator.userAgent.includes("Brave");
      if (isBrave) {
        setError(
          "Brave blocks speech recognition. Enable in brave://settings/privacy or use Chrome."
        );
      } else {
        setError("Speech recognition not supported. Use Chrome or Edge.");
      }
      return;
    }

    const recognition = new SpeechRecognitionAPI();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let currentInterim = "";

      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;

        if (result.isFinal) {
          if (i >= event.resultIndex) {
            finalTranscriptRef.current += text + " ";
          }
        } else {
          currentInterim = text;
        }
      }

      interimTranscriptRef.current = currentInterim;
      const fullTranscript =
        finalTranscriptRef.current + interimTranscriptRef.current;
      setTranscript(fullTranscript.trim());
    };

    recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      if (event.error === "no-speech" || event.error === "aborted") {
        return;
      }
      console.error("Speech recognition error:", event.error);
      setError(`Speech recognition error: ${event.error}`);
    };

    recognition.onend = () => {
      // Auto-restart if still listening
      if (isListening && enabledRef.current) {
        setTimeout(() => {
          try {
            recognitionRef.current?.start();
          } catch {
            // Ignore restart errors
          }
        }, 100);
      }
    };

    recognitionRef.current = recognition;

    return () => {
      recognitionRef.current?.abort();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Audio level analysis for VAD
  const checkAudioLevel = useCallback(() => {
    if (!analyserRef.current) return;
    
    // When disabled (AI speaking), reset VAD state and skip processing
    // This prevents the AI's voice from being detected as user speech
    if (!enabledRef.current) {
      if (isSpeakingRef.current) {
        isSpeakingRef.current = false;
        setIsSpeaking(false);
      }
      // Reset speech detection state so we start fresh when re-enabled
      hasSpokenRef.current = false;
      lastSpeechTimeRef.current = 0;
      return;
    }

    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    // Calculate average volume
    const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
    const normalizedLevel = average / 255;

    const now = Date.now();
    const wasSpeaking = isSpeakingRef.current;

    if (normalizedLevel > speechThreshold) {
      // Speech detected
      lastSpeechTimeRef.current = now;
      if (!wasSpeaking) {
        isSpeakingRef.current = true;
        setIsSpeaking(true);
        if (!hasSpokenRef.current) {
          hasSpokenRef.current = true;
          onSpeechStart?.();
        }
      }
    } else if (wasSpeaking) {
      // Check if silence threshold exceeded
      const silenceDuration = now - lastSpeechTimeRef.current;
      if (silenceDuration >= silenceThreshold && hasSpokenRef.current) {
        // Speech ended - trigger callback with transcript
        isSpeakingRef.current = false;
        setIsSpeaking(false);

        const finalText = (
          finalTranscriptRef.current + interimTranscriptRef.current
        ).trim();

        if (finalText.length > 0) {
          onSpeechEnd?.(finalText);
          // Reset transcript for next utterance
          finalTranscriptRef.current = "";
          interimTranscriptRef.current = "";
          setTranscript("");
          hasSpokenRef.current = false;
        }
      }
    }
  }, [speechThreshold, silenceThreshold, onSpeechEnd, onSpeechStart]);

  const startListening = useCallback(async () => {
    if (!isSupported || isListening) return;

    setError(null);
    finalTranscriptRef.current = "";
    interimTranscriptRef.current = "";
    setTranscript("");
    hasSpokenRef.current = false;
    isSpeakingRef.current = false;

    try {
      // Get microphone stream
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Set up audio analysis
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;

      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);

      // Start speech recognition
      try {
        recognitionRef.current?.start();
      } catch {
        // May already be started
      }

      setIsListening(true);

      // Start VAD checking
      checkIntervalRef.current = setInterval(checkAudioLevel, checkInterval);
    } catch (err) {
      console.error("Failed to start VAD:", err);
      setError("Microphone access required for voice detection.");
    }
  }, [isSupported, isListening, checkAudioLevel, checkInterval]);

  const stopListening = useCallback(() => {
    setIsListening(false);
    setIsSpeaking(false);

    // Stop interval
    if (checkIntervalRef.current) {
      clearInterval(checkIntervalRef.current);
      checkIntervalRef.current = null;
    }

    // Stop speech recognition
    try {
      recognitionRef.current?.stop();
    } catch {
      // Ignore
    }

    // Clean up audio
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  return {
    startListening,
    stopListening,
    transcript,
    isListening,
    isSpeaking,
    isSupported,
    error,
  };
}

export default useVoiceActivityDetection;
