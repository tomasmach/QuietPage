import { cs } from './cs';
import { en } from './en';

export const translations = {
  cs,
  en,
} as const;

export type Language = keyof typeof translations;
export type { Translations } from './cs';
