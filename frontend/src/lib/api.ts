/**
 * API Client with CSRF handling
 * Singleton instance that manages all API requests to Django backend
 */

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean>;
}

class ApiClient {
  private baseURL = '/api/v1';
  private csrfToken: string | null = null;
  private csrfReady: Promise<void>;
  private csrfReadyResolve!: () => void;
  private _isAuthenticated = false;

  constructor() {
    // Create a promise that resolves when CSRF token is ready
    this.csrfReady = new Promise((resolve) => {
      this.csrfReadyResolve = resolve;
    });
    this.fetchCsrfToken();
  }

  /**
   * Get current authentication status
   */
  public get isAuthenticated(): boolean {
    return this._isAuthenticated;
  }

  /**
   * Set authentication status (should only be called by AuthContext)
   */
  public setAuthenticated(value: boolean): void {
    this._isAuthenticated = value;
  }

  /**
   * Returns a promise that resolves when the CSRF token has been fetched
   * Use this to ensure the API client is ready before making requests
   */
  public async ready(): Promise<void> {
    return this.csrfReady;
  }

  /**
   * Fetch CSRF token from Django backend with retry logic
   */
  private async fetchCsrfToken(): Promise<void> {
    const maxRetries = 3;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        const response = await fetch('/api/v1/auth/csrf/', {
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          this.csrfToken = data.csrfToken;
          this.csrfReadyResolve();
          return;
        }

        // Treat non-OK responses as failures
        const responseBody = await response.text().catch(() => '');
        const errorMessage = responseBody || response.statusText || 'Unknown error';
        lastError = new Error(
          `HTTP ${response.status}: ${errorMessage}`
        );

        if (import.meta.env.DEV) {
          console.error(`CSRF token fetch attempt ${attempt + 1} failed:`, lastError);
        }

        // Wait before retry (exponential backoff)
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 100));
        }
      } catch (error) {
        lastError = error as Error;
        if (import.meta.env.DEV) {
          console.error(`CSRF token fetch attempt ${attempt + 1} failed:`, error);
        }
        // Wait before retry (exponential backoff)
        if (attempt < maxRetries - 1) {
          await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 100));
        }
      }
    }

    // All retries failed - resolve anyway, will fallback to cookie
    if (import.meta.env.DEV && lastError) {
      console.error('All CSRF token fetch attempts failed, falling back to cookie:', lastError);
    }
    this.csrfReadyResolve();
  }

  /**
   * Get CSRF token from cookie as fallback
   */
  private getCsrfTokenFromCookie(): string | null {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');

    for (const cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        return trimmed.substring(name.length + 1);
      }
    }

    return null;
  }

  /**
   * Build request headers with CSRF token
   */
  private buildHeaders(options: RequestOptions = {}): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Merge existing headers
    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    // Add CSRF token to ALL requests (DRF SessionAuthentication requires it)
    const token = this.csrfToken || this.getCsrfTokenFromCookie();
    if (token) {
      headers['X-CSRFToken'] = token;
    }

    return headers;
  }

  /**
   * Build URL with query parameters
   */
  private buildUrl(endpoint: string, params?: Record<string, string | number | boolean>): string {
    // Ensure endpoint doesn't start with slash to avoid overriding base path
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
    const fullPath = `${this.baseURL}/${cleanEndpoint}`;
    const url = new URL(fullPath, window.location.origin);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    return url.toString();
  }

  /**
   * Base request method with timeout
   */
  private async request<T>(
    endpoint: string,
    options: RequestOptions = {},
    timeout: number = 30000
  ): Promise<T> {
    const { params, ...fetchOptions } = options;

    const url = this.buildUrl(endpoint, params);
    const headers = this.buildHeaders(options);

    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: 'include',
        signal: controller.signal,
      });

      // Handle HTTP errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Create error with full error data preserved
        // For register/login endpoints, the error is in errorData.errors or direct in errorData
        const errorPayload = errorData.errors || errorData;
        // Include status code in error message so handlers can check for specific HTTP errors (e.g., 404)
        const error = new Error(`${response.status}: ${JSON.stringify(errorPayload)}`);

        // Suppress console errors for expected 403 on auth check endpoints
        // (These are normal when user is not authenticated)
        const isAuthCheckEndpoint = endpoint.includes('/auth/me');
        const is403 = response.status === 403;

        if (isAuthCheckEndpoint && is403) {
          // Silent error - don't log to console
          throw error;
        }

        throw error;
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T;
      }

      return response.json();
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, params?: Record<string, string | number | boolean>): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'GET',
      params,
    });
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
export const api = new ApiClient();

/**
 * Parse API error message to extract the JSON payload
 * Error format: "STATUS_CODE: {json_payload}"
 */
export function parseApiError(error: Error): Record<string, unknown> {
  try {
    const colonIndex = error.message.indexOf(': ');
    if (colonIndex !== -1) {
      const jsonPart = error.message.slice(colonIndex + 2);
      return JSON.parse(jsonPart);
    }
    return JSON.parse(error.message);
  } catch {
    return {};
  }
}
