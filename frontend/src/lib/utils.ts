import { type ClassValue, clsx } from 'clsx';

/**
 * Utility function for merging classnames
 * Combines clsx for conditional classes
 */
export function cn(...inputs: ClassValue[]): string {
  return clsx(inputs);
}

export type SupportedLocale = 'cs' | 'en';

/**
 * Parses an ISO date string (YYYY-MM-DD) as a local date.
 * Avoids timezone shifts that occur when using new Date(dateString).
 */
export function parseLocalDate(dateString: string): Date {
  const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (match) {
    return new Date(parseInt(match[1]), parseInt(match[2]) - 1, parseInt(match[3]));
  }
  return new Date(dateString);
}

/**
 * Formats a date string to a localized format.
 * Parses ISO date string (YYYY-MM-DD) as local date to avoid timezone shifts.
 */
export function formatLocalizedDate(
  dateString: string,
  language: SupportedLocale,
  options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' }
): string {
  const date = parseLocalDate(dateString);
  const locale = language === 'cs' ? 'cs-CZ' : 'en-US';
  return date.toLocaleDateString(locale, options);
}

/**
 * Formats a number according to locale conventions.
 */
export function formatLocalizedNumber(num: number, language: SupportedLocale): string {
  const locale = language === 'cs' ? 'cs-CZ' : 'en-US';
  return num.toLocaleString(locale);
}

/**
 * Returns the locale string for a given language.
 */
export function getLocale(language: SupportedLocale): string {
  return language === 'cs' ? 'cs-CZ' : 'en-US';
}
