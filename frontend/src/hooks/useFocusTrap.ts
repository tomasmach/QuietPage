import { useEffect, useRef } from 'react';

type FocusableElement = HTMLElement;

/**
 * Custom hook to trap focus within a container element
 * Implements WCAG 2.1 SC 2.4.3 (Focus Order)
 */
export function useFocusTrap(isActive: boolean) {
  const containerRef = useRef<HTMLElement>(null);
  const previousActiveElementRef = useRef<FocusableElement | null>(null);

  useEffect(() => {
    if (!isActive) return;

    const container = containerRef.current;
    if (!container) return;

    // Store the previously focused element
    previousActiveElementRef.current = document.activeElement as FocusableElement;

    // Get all focusable elements within the container
    const focusableElements = container.querySelectorAll<FocusableElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"]), [contenteditable], audio[controls], video[controls], details>summary'
    );

    if (focusableElements.length === 0) return;

    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    // Focus the first element
    firstFocusable.focus();

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      // If Shift+Tab and focus is on first element, wrap to last
      if (e.shiftKey && document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
      // If Tab (no Shift) and focus is on last element, wrap to first
      else if (!e.shiftKey && document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    };

    container.addEventListener('keydown', handleTab);

    return () => {
      container.removeEventListener('keydown', handleTab);
      // Restore focus to the previously active element
      previousActiveElementRef.current?.focus();
    };
  }, [isActive]);

  return containerRef;
}

/**
 * Custom hook to handle body scroll lock and Escape key
 */
export function useOverlay(isOpen: boolean, onClose: () => void) {
  useEffect(() => {
    if (!isOpen) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    // Capture original overflow value
    const originalOverflow = document.body.style.overflow;

    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = originalOverflow;
    };
  }, [isOpen, onClose]);
}
