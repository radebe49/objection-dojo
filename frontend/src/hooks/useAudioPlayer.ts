"use client";

import { useState, useCallback, useRef, useEffect } from "react";

interface UseAudioPlayerOptions {
  onEnded?: () => void;
}

interface UseAudioPlayerReturn {
  play: (audioBase64: string) => void;
  stop: () => void;
  isPlaying: boolean;
}

/**
 * Custom hook for playing base64-encoded audio.
 * 
 * **Feature: objection-dojo, Requirements 3.6, 6.2**
 * - Accepts base64 audio string
 * - Creates Audio element with data URI
 * - Exposes play(), isPlaying, onEnded callback
 */
export function useAudioPlayer(
  options: UseAudioPlayerOptions = {}
): UseAudioPlayerReturn {
  const { onEnded } = options;
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const onEndedRef = useRef(onEnded);

  // Keep onEnded callback ref updated
  useEffect(() => {
    onEndedRef.current = onEnded;
  }, [onEnded]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = "";
        audioRef.current = null;
      }
    };
  }, []);

  const play = useCallback((audioBase64: string) => {
    // Stop any currently playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.src = "";
    }

    // Create new audio element with data URI
    const audio = new Audio(`data:audio/mpeg;base64,${audioBase64}`);
    audioRef.current = audio;

    // Set up event handlers
    audio.onplay = () => {
      setIsPlaying(true);
    };

    audio.onended = () => {
      setIsPlaying(false);
      if (onEndedRef.current) {
        onEndedRef.current();
      }
    };

    audio.onerror = (e) => {
      console.error("Audio playback error:", e);
      setIsPlaying(false);
      if (onEndedRef.current) {
        onEndedRef.current();
      }
    };

    audio.onpause = () => {
      // Only set isPlaying to false if audio has ended or was stopped
      // This prevents false negatives during normal playback
      if (audio.ended || audio.currentTime === 0) {
        setIsPlaying(false);
      }
    };

    // Start playback
    audio.play().catch((err) => {
      console.error("Failed to play audio:", err);
      setIsPlaying(false);
      if (onEndedRef.current) {
        onEndedRef.current();
      }
    });
  }, []);

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = "";
      setIsPlaying(false);
    }
  }, []);

  return {
    play,
    stop,
    isPlaying,
  };
}

export default useAudioPlayer;
