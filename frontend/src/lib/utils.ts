import { type ClassValue, clsx } from 'clsx';

/**
 * Utility function for merging classnames
 * Combines clsx for conditional classes
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
