/**
 * Production-safe logger utility with configurable error handling.
 * In development: logs to console
 * In production: sends to configured error handler or sanitized console.error fallback
 */

const isDev = import.meta.env.DEV;

// Type for the error handler callback
type ErrorHandler = (message: string, ...args: unknown[]) => void;

// Configuration object
const config = {
  errorHandler: null as ErrorHandler | null,
};

/**
 * Set a custom error handler for production errors.
 * Use this to integrate with error tracking services like Sentry or LogRocket.
 *
 * @example
 * ```typescript
 * import * as Sentry from '@sentry/react';
 * import { setErrorHandler } from '@/utils/logger';
 *
 * setErrorHandler((message, ...args) => {
 *   Sentry.captureException(new Error(message), {
 *     extra: { args },
 *   });
 * });
 * ```
 */
export const setErrorHandler = (handler: ErrorHandler | null): void => {
  config.errorHandler = handler;
};

/**
 * Sanitize arguments to remove sensitive data before logging.
 * Removes common sensitive field patterns (password, token, key, secret, etc.)
 */
const sanitizeArgs = (args: unknown[]): unknown[] => {
  const sensitiveKeys = ['password', 'token', 'key', 'secret', 'authorization', 'auth'];

  const sanitizeValue = (value: unknown): unknown => {
    // Handle null/undefined
    if (value === null || value === undefined) {
      return value;
    }

    // Handle arrays recursively
    if (Array.isArray(value)) {
      return value.map(sanitizeValue);
    }

    // Handle Error objects
    if (value instanceof Error) {
      return {
        name: value.name,
        message: value.message,
        stack: value.stack,
      };
    }

    // Handle plain objects recursively
    if (typeof value === 'object') {
      const sanitized: Record<string, unknown> = {};
      for (const key of Object.keys(value)) {
        if (sensitiveKeys.some((sensitive) => key.toLowerCase().includes(sensitive))) {
          sanitized[key] = '[REDACTED]';
        } else {
          sanitized[key] = sanitizeValue((value as Record<string, unknown>)[key]);
        }
      }
      return sanitized;
    }

    // Primitive values pass through
    return value;
  };

  return args.map(sanitizeValue);
};

export const logger = {
  /**
   * Log error messages.
   * In development: logs to console.error
   * In production: sends to configured error handler, or sanitized console.error if no handler set
   */
  error: (message: string, ...args: unknown[]): void => {
    if (isDev) {
      console.error(message, ...args);
    } else {
      // Production error handling: use configured handler or fallback to sanitized console.error
      if (config.errorHandler) {
        config.errorHandler(message, ...args);
      } else {
        // Fallback: log to console.error with sanitized args to prevent data leakage
        const sanitized = sanitizeArgs(args);
        console.error(message, ...sanitized);
      }
    }
  },

  /**
   * Log warning messages (only in development)
   */
  warn: (message: string, ...args: unknown[]): void => {
    if (isDev) {
      console.warn(message, ...args);
    }
  },

  /**
   * Log info messages (only in development)
   */
  info: (message: string, ...args: unknown[]): void => {
    if (isDev) {
      console.info(message, ...args);
    }
  },

  /**
   * Log debug messages (only in development)
   */
  debug: (message: string, ...args: unknown[]): void => {
    if (isDev) {
      console.log(message, ...args);
    }
  },
};

export default logger;
