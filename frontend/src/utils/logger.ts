/**
 * Production-safe logger utility.
 * Only logs in development mode to prevent information disclosure.
 */

const isDev = import.meta.env.DEV;

export const logger = {
  /**
   * Log error messages (only in development)
   */
  error: (message: string, ...args: unknown[]): void => {
    if (isDev) {
      console.error(message, ...args);
    }
    // V produkci můžeme případně poslat na error tracking službu (Sentry, etc.)
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
