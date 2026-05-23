/**
 * Type definitions for the Electron API exposed via preload script.
 * This provides type safety when accessing window.electronAPI in the renderer.
 */

interface OllamaStatus {
  available: boolean;
  models: string[];
}

interface AppSettings {
  aiProvider: string;
  ollamaUrl: string;
  ollamaModel: string;
  openaiApiKey: string;
  geminiApiKey: string;
  theme: string;
  autoUpdate: boolean;
}

interface UpdateInfo {
  version: string;
  releaseDate: string;
  releaseNotes?: string;
}

interface ElectronAPI {
  // Settings
  getSettings(): Promise<AppSettings>;
  saveSettings(settings: Partial<AppSettings>): Promise<{ success: boolean }>;
  
  // Backend
  getBackendPort(): Promise<number | null>;
  
  // App info
  getAppVersion(): Promise<string>;
  getUserDataPath(): Promise<string>;
  
  // Ollama
  checkOllamaStatus(): Promise<OllamaStatus>;
  
  // File operations
  selectFile(options?: { filters?: Array<{ name: string; extensions: string[] }> }): Promise<string[]>;
  
  // External links
  openExternalLink(url: string): void;
  
  // Updates
  installUpdate(): void;
  onUpdateAvailable(callback: (info: UpdateInfo) => void): void;
  onUpdateDownloaded(callback: (info: UpdateInfo) => void): void;
  
  // Platform info
  platform: 'win32' | 'darwin' | 'linux';
  arch: string;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

export {};
