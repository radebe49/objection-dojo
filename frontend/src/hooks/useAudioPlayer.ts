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
 * **Feature: dealfu, Requirements 3.6, 6.2**
 * - Accepts base64 audio string
 * - Uses AudioContext for lower latency playback
 * - Exposes play(), isPlaying, onEnded callback
 * 
 * Performance: Reuses AudioContext to avoid initialization overhead (~30-50ms saved)
 */
export function useAudioPlayer(
  options: UseAudioPlayerOptions = {}
): UseAudioPlayerReturn {
  const { onEnded } = options;
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  
  // Use AudioContext for lower latency (reused across plays)
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceNodeRef = useRef<AudioBufferSourceNode | null>(null);
  const onEndedRef = useRef(onEnded);

  // Keep onEnded callback ref updated
  useEffect(() => {
    onEndedRef.current = onEnded;
  }, [onEnded]);

  // Initialize AudioContext lazily (must be after user interaction)
  const getAudioContext = useCallback(() => {
    if (!audioContextRef.current || audioContextRef.current.state === "closed") {
      audioContextRef.current = new AudioContext();
    }
    // Resume if suspended (browser autoplay policy)
    if (audioContextRef.current.state === "suspended") {
      audioContextRef.current.resume();
    }
    return audioContextRef.current;
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (sourceNodeRef.current) {
        try {
          sourceNodeRef.current.stop();
        } catch {
          // Ignore if already stopped
        }
        sourceNodeRef.current = null;
      }
      if (audioContextRef.current && audioContextRef.current.state !== "closed") {
        audioContextRef.current.close();
        audioContextRef.current = null;
      }
    };
  }, []);

  const play = useCallback(async (audioBase64: string) => {
    // Stop any currently playing audio
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
      } catch {
        // Ignore if already stopped
      }
      sourceNodeRef.current = null;
    }

    try {
      const audioContext = getAudioContext();
      
      // Decode base64 to ArrayBuffer
      const binaryString = atob(audioBase64);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Decode audio data
      const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);
      
      // Create and configure source node
      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);
      
      sourceNodeRef.current = source;
      setIsPlaying(true);
      
      // Handle playback end
      source.onended = () => {
        setIsPlaying(false);
        sourceNodeRef.current = null;
        if (onEndedRef.current) {
          onEndedRef.current();
        }
      };
      
      // Start playback immediately
      source.start(0);
      
    } catch (err) {
      console.error("Audio playback error:", err);
      setIsPlaying(false);
      if (onEndedRef.current) {
        onEndedRef.current();
      }
    }
  }, [getAudioContext]);

  const stop = useCallback(() => {
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
      } catch {
        // Ignore if already stopped
      }
      sourceNodeRef.current = null;
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
