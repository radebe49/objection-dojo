import { describe, it, expect, vi } from "vitest";
import * as fc from "fast-check";
import { render, screen, fireEvent } from "@testing-library/react";
import ActionButton from "./ActionButton";

describe("ActionButton", () => {
  /**
   * **Feature: dealfu, Property 6: Audio Mutex - Button Disabled During Playback**
   * 
   * *For any* state where audio is currently playing, the Action Button SHALL be in disabled state.
   * 
   * **Validates: Requirements 6.1**
   */
  describe("Property 6: Audio Mutex - Button Disabled During Playback", () => {
    it("should be disabled when state is 'disabled' (property test)", () => {
      // Generate sequences of render attempts with disabled state
      fc.assert(
        fc.property(fc.nat(100), () => {
          const onClick = vi.fn();
          const { unmount } = render(
            <ActionButton state="disabled" onClick={onClick} />
          );

          const button = screen.getByRole("button");
          
          // Button should be disabled
          expect(button).toBeDisabled();
          expect(button).toHaveAttribute("aria-disabled", "true");
          
          // Clicking should not trigger onClick
          fireEvent.click(button);
          expect(onClick).not.toHaveBeenCalled();

          unmount();
        }),
        { numRuns: 100 }
      );
    });

    it("should have disabled styling when in disabled state", () => {
      const onClick = vi.fn();
      render(<ActionButton state="disabled" onClick={onClick} />);

      const button = screen.getByRole("button");
      expect(button).toHaveClass("cursor-not-allowed");
      expect(button).toHaveClass("opacity-60");
    });

    it("should not be disabled when in idle state", () => {
      const onClick = vi.fn();
      render(<ActionButton state="idle" onClick={onClick} />);

      const button = screen.getByRole("button");
      expect(button).not.toBeDisabled();
    });

    it("should not be disabled when in recording state", () => {
      const onClick = vi.fn();
      render(<ActionButton state="recording" onClick={onClick} />);

      const button = screen.getByRole("button");
      expect(button).not.toBeDisabled();
    });
  });

  /**
   * **Feature: dealfu, Property 7: Disabled Button Ignores Input**
   * 
   * *For any* sequence of tap events while the Action Button is disabled,
   * the button state SHALL remain unchanged.
   * 
   * **Validates: Requirements 6.3**
   */
  describe("Property 7: Disabled Button Ignores Input", () => {
    it("should ignore any number of clicks when disabled (property test)", () => {
      // Generate random number of click attempts
      fc.assert(
        fc.property(fc.integer({ min: 1, max: 50 }), (numClicks) => {
          const onClick = vi.fn();
          const { unmount } = render(
            <ActionButton state="disabled" onClick={onClick} />
          );

          const button = screen.getByRole("button");

          // Perform multiple clicks
          for (let i = 0; i < numClicks; i++) {
            fireEvent.click(button);
          }

          // onClick should never have been called
          expect(onClick).not.toHaveBeenCalled();

          unmount();
        }),
        { numRuns: 100 }
      );
    });

    it("should call onClick when not disabled", () => {
      const onClick = vi.fn();
      render(<ActionButton state="idle" onClick={onClick} />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      expect(onClick).toHaveBeenCalledTimes(1);
    });

    it("should call onClick when in recording state", () => {
      const onClick = vi.fn();
      render(<ActionButton state="recording" onClick={onClick} />);

      const button = screen.getByRole("button");
      fireEvent.click(button);

      expect(onClick).toHaveBeenCalledTimes(1);
    });
  });

  describe("State rendering", () => {
    it("should render mic icon in idle state", () => {
      render(<ActionButton state="idle" onClick={() => {}} />);
      // Updated to match new descriptive ARIA label
      expect(screen.getByLabelText("Tap to start recording your sales pitch")).toBeInTheDocument();
    });

    it("should render stop icon in recording state", () => {
      render(<ActionButton state="recording" onClick={() => {}} />);
      // Updated to match new descriptive ARIA label
      expect(screen.getByLabelText("Recording in progress. Tap to stop recording and send your message")).toBeInTheDocument();
    });

    it("should render disabled label when disabled", () => {
      render(<ActionButton state="disabled" onClick={() => {}} />);
      // Updated to match new descriptive ARIA label
      expect(screen.getByLabelText("Microphone button disabled, waiting for audio to finish")).toBeInTheDocument();
    });

    it("should render loading label when loading", () => {
      render(<ActionButton state="disabled" onClick={() => {}} isLoading={true} />);
      // Test the loading state ARIA label
      expect(screen.getByLabelText("Processing your message, please wait")).toBeInTheDocument();
    });
  });
});
