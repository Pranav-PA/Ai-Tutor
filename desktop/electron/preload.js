/**
 * Preload script - Exposes safe APIs to the renderer process
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Settings
  getSettings: () => ipcRenderer.invoke('get-settings'),
  saveSettings: (settings) => ipcRenderer.invoke('save-settings', settings),
  
  // Backend
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getUserDataPath: () => ipcRenderer.invoke('get-user-data-path'),
  
  // Ollama
  checkOllamaStatus: () => ipcRenderer.invoke('check-ollama-status'),
  
  // File operations
  selectFile: (options) => ipcRenderer.invoke('select-file', options),
  
  // External links
  openExternalLink: (url) => ipcRenderer.invoke('open-external-link', url),
  
  // Updates
  installUpdate: () => ipcRenderer.invoke('install-update'),
  onUpdateAvailable: (callback) => ipcRenderer.on('update-available', (_, info) => callback(info)),
  onUpdateDownloaded: (callback) => ipcRenderer.on('update-downloaded', (_, info) => callback(info)),
  
  // Platform info
  platform: process.platform,
  arch: process.arch
});
