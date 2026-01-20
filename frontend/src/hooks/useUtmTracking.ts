/**
 * Hook for capturing and storing UTM tracking parameters.
 *
 * Captures UTM params from URL on first visit and stores them in localStorage.
 * Returns the stored UTM data for use during registration.
 */

const UTM_STORAGE_KEY = 'quietpage_utm';

export interface UtmData {
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  referrer: string;
}

/**
 * Get UTM parameters from current URL
 */
function getUtmFromUrl(): Partial<UtmData> {
  const params = new URLSearchParams(window.location.search);
  const utm: Partial<UtmData> = {};

  const source = params.get('utm_source');
  const medium = params.get('utm_medium');
  const campaign = params.get('utm_campaign');

  if (source) utm.utm_source = source;
  if (medium) utm.utm_medium = medium;
  if (campaign) utm.utm_campaign = campaign;

  return utm;
}

/**
 * Get stored UTM data from localStorage
 */
function getStoredUtm(): Partial<UtmData> | null {
  try {
    const stored = localStorage.getItem(UTM_STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch {
    // Ignore parse errors
  }
  return null;
}

/**
 * Store UTM data in localStorage
 */
function storeUtm(data: Partial<UtmData>): void {
  try {
    localStorage.setItem(UTM_STORAGE_KEY, JSON.stringify(data));
  } catch {
    // Ignore storage errors (e.g., private browsing)
  }
}

/**
 * Clear stored UTM data (call after successful registration)
 */
export function clearUtmData(): void {
  try {
    localStorage.removeItem(UTM_STORAGE_KEY);
  } catch {
    // Ignore errors
  }
}

/**
 * Capture UTM params from URL and store them.
 * Call this on app initialization or landing page load.
 */
export function captureUtmParams(): void {
  const urlUtm = getUtmFromUrl();

  // Only capture if we have UTM params in URL
  if (Object.keys(urlUtm).length === 0) {
    return;
  }

  // Get existing stored data
  const existingUtm = getStoredUtm() || {};

  // Merge: URL params take priority, but keep existing referrer if not in URL
  const merged: Partial<UtmData> = {
    ...existingUtm,
    ...urlUtm,
  };

  // Capture referrer if not already stored and document.referrer is external
  if (!merged.referrer && document.referrer) {
    try {
      const referrerUrl = new URL(document.referrer);
      const currentHost = window.location.hostname;
      // Only store if referrer is from different domain
      if (referrerUrl.hostname !== currentHost) {
        merged.referrer = document.referrer;
      }
    } catch {
      // Invalid URL, ignore
    }
  }

  storeUtm(merged);
}

/**
 * Hook to get current UTM data for registration
 */
export function useUtmTracking(): Partial<UtmData> {
  // First try to get from URL (in case user is on landing page with UTM)
  const urlUtm = getUtmFromUrl();

  // Then get stored data
  const storedUtm = getStoredUtm();

  // Merge: URL takes priority
  const merged: Partial<UtmData> = {
    ...storedUtm,
    ...urlUtm,
  };

  // Capture referrer if we have UTM but no referrer yet
  if (Object.keys(merged).length > 0 && !merged.referrer && document.referrer) {
    try {
      const referrerUrl = new URL(document.referrer);
      const currentHost = window.location.hostname;
      if (referrerUrl.hostname !== currentHost) {
        merged.referrer = document.referrer;
      }
    } catch {
      // Invalid URL, ignore
    }
  }

  return merged;
}
