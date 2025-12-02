/**
 * Validates transcript input before sending to the API.
 * 
 * **Feature: objection-dojo, Requirements 2.4, 2.6**
 * - Rejects empty, null, or whitespace-only strings
 * - Accepts strings with at least one non-whitespace character
 */

/**
 * Checks if a transcript is valid (non-empty and contains non-whitespace characters).
 * @param transcript - The transcript string to validate
 * @returns true if the transcript is valid, false otherwise
 */
export function isValidTranscript(transcript: string | null | undefined): boolean {
  if (transcript === null || transcript === undefined) {
    return false;
  }
  
  // Trim and check if there's any content left
  return transcript.trim().length > 0;
}

/**
 * Determines if an API call should be triggered based on transcript validity.
 * @param transcript - The transcript string to check
 * @returns true if API should be called, false otherwise
 */
export function shouldTriggerApiCall(transcript: string | null | undefined): boolean {
  return isValidTranscript(transcript);
}
