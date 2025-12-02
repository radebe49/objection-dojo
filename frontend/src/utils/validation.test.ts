import { describe, it, expect } from "vitest";
import * as fc from "fast-check";
import { isValidTranscript, shouldTriggerApiCall } from "./validation";

describe("Transcript Validation", () => {
  /**
   * **Feature: objection-dojo, Property 1: Whitespace Input Rejection**
   * 
   * *For any* string that is empty, null, or contains only whitespace characters,
   * the system SHALL reject it without sending to the backend API.
   * 
   * **Validates: Requirements 2.4**
   */
  describe("Property 1: Whitespace Input Rejection", () => {
    it("should reject null input", () => {
      expect(isValidTranscript(null)).toBe(false);
      expect(shouldTriggerApiCall(null)).toBe(false);
    });

    it("should reject undefined input", () => {
      expect(isValidTranscript(undefined)).toBe(false);
      expect(shouldTriggerApiCall(undefined)).toBe(false);
    });

    it("should reject empty string", () => {
      expect(isValidTranscript("")).toBe(false);
      expect(shouldTriggerApiCall("")).toBe(false);
    });

    it("should reject any whitespace-only string (property test)", () => {
      // Generate strings containing only whitespace characters
      const whitespaceArbitrary = fc
        .array(fc.constantFrom(" ", "\t", "\n", "\r", "\f", "\v"))
        .map((chars) => chars.join(""));

      fc.assert(
        fc.property(whitespaceArbitrary, (whitespaceString) => {
          // All whitespace-only strings should be rejected
          expect(isValidTranscript(whitespaceString)).toBe(false);
          expect(shouldTriggerApiCall(whitespaceString)).toBe(false);
        }),
        { numRuns: 100 }
      );
    });
  });

  /**
   * **Feature: objection-dojo, Property 2: Valid Text Triggers API Call**
   * 
   * *For any* string that contains at least one non-whitespace character,
   * the system SHALL send it to the Backend API.
   * 
   * **Validates: Requirements 2.6**
   */
  describe("Property 2: Valid Text Triggers API Call", () => {
    it("should accept any string with at least one non-whitespace character (property test)", () => {
      // Generate strings that have at least one non-whitespace character
      // Use constantFrom with alphanumeric characters
      const nonWhitespaceChar = fc.constantFrom(
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
        "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
      );
      const validStringArbitrary = fc
        .tuple(
          fc.array(fc.constantFrom(" ", "\t", "\n")).map((a) => a.join("")), // optional leading whitespace
          nonWhitespaceChar, // at least one non-whitespace char
          fc.array(fc.constantFrom(" ", "\t", "\n")).map((a) => a.join("")) // optional trailing whitespace
        )
        .map(([prefix, char, suffix]) => prefix + char + suffix);

      fc.assert(
        fc.property(validStringArbitrary, (validString) => {
          // All strings with at least one non-whitespace char should be accepted
          expect(isValidTranscript(validString)).toBe(true);
          expect(shouldTriggerApiCall(validString)).toBe(true);
        }),
        { numRuns: 100 }
      );
    });

    it("should accept simple valid inputs", () => {
      expect(isValidTranscript("hello")).toBe(true);
      expect(isValidTranscript("  hello  ")).toBe(true);
      expect(isValidTranscript("a")).toBe(true);
      expect(shouldTriggerApiCall("hello")).toBe(true);
    });
  });
});
