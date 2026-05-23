/**
 * API Configuration for Desktop App
 * 
 * Resolves the backend API URL dynamically based on whether
 * we're running in Electron (desktop) or browser (dev) context.
 */

// Detect if running inside Electron
const isElectron = typeof window !== 'undefined' && !!(window as any).electronAPI;

/**
 * Get the API base URL
 * In Electron: dynamically resolved from the backend port
 * In browser/dev: uses relative /api path (handled by Next.js rewrites)
 */
export async function getApiBaseUrl(): Promise<string> {
  if (isElectron) {
    try {
      const port = await (window as any).electronAPI.getBackendPort();
      if (port) {
        return `http://127.0.0.1:${port}/api`;
      }
    } catch (e) {
      console.warn('Failed to get backend port from Electron:', e);
    }
  }
  // Fallback for development/browser mode
  return '/api';
}

// Cached base URL (resolved once)
let cachedBaseUrl: string | null = null;

export async function resolveApiBase(): Promise<string> {
  if (!cachedBaseUrl) {
    cachedBaseUrl = await getApiBaseUrl();
  }
  return cachedBaseUrl;
}

// Synchronous fallback (for initial render)
export function getApiBaseSync(): string {
  if (cachedBaseUrl) return cachedBaseUrl;
  if (isElectron) {
    // Will be resolved async, use localhost default
    return 'http://127.0.0.1:18080/api';
  }
  return '/api';
}

export { isElectron };
