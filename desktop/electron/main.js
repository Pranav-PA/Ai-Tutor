/**
 * AI Semester Companion - Electron Main Process
 * 
 * Manages the application lifecycle, spawns backend process,
 * and serves the frontend UI.
 */
const { app, BrowserWindow, ipcMain, dialog, shell, Menu, Tray, nativeImage } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const log = require('electron-log');
const Store = require('electron-store');
const { autoUpdater } = require('electron-updater');

// Local modules
const { BackendManager } = require('./backend-manager');
const { createMenu } = require('./menu');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';
autoUpdater.logger = log;

// App store for settings
const store = new Store({
  defaults: {
    windowBounds: { width: 1400, height: 900 },
    aiProvider: 'gemini',
    ollamaUrl: 'http://localhost:11434',
    ollamaModel: 'llama3.1',
    openaiApiKey: '',
    geminiApiKey: '',
    theme: 'dark',
    autoUpdate: true,
    firstRun: true
  }
});

// Global references
let mainWindow = null;
let splashWindow = null;
let backendManager = null;
let tray = null;

// Determine if we're in development
const isDev = process.env.NODE_ENV === 'development';

// Paths
const getResourcePath = (...segments) => {
  if (isDev) {
    return path.join(__dirname, '..', ...segments);
  }
  return path.join(process.resourcesPath, ...segments);
};

const getUserDataPath = (...segments) => {
  return path.join(app.getPath('userData'), ...segments);
};

/**
 * Create the splash/loading screen
 */
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 350,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    resizable: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.center();
}

/**
 * Create the main application window
 */
function createMainWindow() {
  const { width, height } = store.get('windowBounds');

  mainWindow = new BrowserWindow({
    width,
    height,
    minWidth: 1024,
    minHeight: 680,
    show: false,
    frame: true,
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    backgroundColor: '#0f0f23',
    icon: path.join(__dirname, '..', 'build', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    }
  });

  // Save window bounds on resize
  mainWindow.on('resize', () => {
    const bounds = mainWindow.getBounds();
    store.set('windowBounds', { width: bounds.width, height: bounds.height });
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  return mainWindow;
}

/**
 * Load the frontend into the main window
 */
async function loadFrontend(backendPort, frontendPort) {
  if (isDev) {
    // In dev mode, load from Next.js dev server
    mainWindow.loadURL('http://localhost:38173');
    mainWindow.webContents.openDevTools();
  } else {
    // In production, load from the Next.js standalone server
    mainWindow.loadURL(`http://localhost:${frontendPort}`);
  }
}

/**
 * Initialize the application
 */
async function initializeApp() {
  log.info('Starting AI Semester Companion...');

  // Create splash screen
  createSplashWindow();

  // Create main window (hidden)
  createMainWindow();

  // Create application menu
  const menu = createMenu(mainWindow, store);
  Menu.setApplicationMenu(menu);

  // Ensure user data directories exist
  const dataDirs = ['uploads', 'vectors', 'generated', 'progress', 'cache', 'courses'];
  dataDirs.forEach(dir => {
    const dirPath = getUserDataPath('app-data', dir);
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
  });

  // Start the backend
  backendManager = new BackendManager({
    isDev,
    resourcePath: isDev ? path.join(__dirname, '..', '..') : process.resourcesPath,
    userDataPath: app.getPath('userData'),
    store,
    log,
    onStatusUpdate: (status) => {
      if (splashWindow && !splashWindow.isDestroyed()) {
        splashWindow.webContents.send('status-update', status);
      }
    }
  });

  try {
    const backendPort = await backendManager.start();
    log.info(`Backend started on port ${backendPort}`);

    // Start the frontend server (Next.js standalone)
    let frontendPort = backendPort; // fallback
    if (!isDev) {
      const { FrontendManager } = require('./frontend-manager');
      global.frontendManager = new FrontendManager({
        resourcePath: process.resourcesPath,
        backendPort,
        log,
        onStatusUpdate: (status) => {
          if (splashWindow && !splashWindow.isDestroyed()) {
            splashWindow.webContents.send('status-update', status);
          }
        }
      });
      frontendPort = await global.frontendManager.start();
      log.info(`Frontend started on port ${frontendPort}`);
    }

    // Load frontend
    await loadFrontend(backendPort, isDev ? 38173 : frontendPort);

    // Show main window and close splash
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
      splashWindow = null;
    }

    // Check for updates
    if (store.get('autoUpdate')) {
      autoUpdater.checkForUpdatesAndNotify();
    }

  } catch (error) {
    log.error('Failed to start application:', error);
    if (splashWindow && !splashWindow.isDestroyed()) {
      splashWindow.close();
    }
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start the application.\n\nError: ${error.message}\n\nPlease try restarting the application.`
    );
    app.quit();
  }
}

// ===== App Lifecycle =====

app.whenReady().then(initializeApp);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createMainWindow();
    if (backendManager && backendManager.isRunning()) {
      loadFrontend(backendManager.getPort());
      mainWindow.show();
    }
  }
});

app.on('before-quit', async () => {
  log.info('Application quitting...');
  if (global.frontendManager) {
    await global.frontendManager.stop();
  }
  if (backendManager) {
    await backendManager.stop();
  }
});

// ===== IPC Handlers =====

ipcMain.handle('get-settings', () => {
  return {
    aiProvider: store.get('aiProvider'),
    ollamaUrl: store.get('ollamaUrl'),
    ollamaModel: store.get('ollamaModel'),
    openaiApiKey: store.get('openaiApiKey') ? '••••••••' : '',
    geminiApiKey: store.get('geminiApiKey') ? '••••••••' : '',
    theme: store.get('theme'),
    autoUpdate: store.get('autoUpdate')
  };
});

ipcMain.handle('save-settings', (event, settings) => {
  if (settings.aiProvider) store.set('aiProvider', settings.aiProvider);
  if (settings.ollamaUrl) store.set('ollamaUrl', settings.ollamaUrl);
  if (settings.ollamaModel) store.set('ollamaModel', settings.ollamaModel);
  if (settings.openaiApiKey !== undefined && settings.openaiApiKey !== '••••••••') {
    store.set('openaiApiKey', settings.openaiApiKey);
  }
  if (settings.geminiApiKey !== undefined && settings.geminiApiKey !== '••••••••') {
    store.set('geminiApiKey', settings.geminiApiKey);
  }
  if (settings.theme) store.set('theme', settings.theme);
  if (settings.autoUpdate !== undefined) store.set('autoUpdate', settings.autoUpdate);

  // Notify backend of settings change
  if (backendManager && backendManager.isRunning()) {
    backendManager.updateSettings(store);
  }
  return { success: true };
});

ipcMain.handle('get-backend-port', () => {
  return backendManager ? backendManager.getPort() : null;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('check-ollama-status', async () => {
  const ollamaUrl = store.get('ollamaUrl');
  try {
    const response = await fetch(`${ollamaUrl}/api/tags`);
    if (response.ok) {
      const data = await response.json();
      return { available: true, models: data.models || [] };
    }
    return { available: false, models: [] };
  } catch {
    return { available: false, models: [] };
  }
});

ipcMain.handle('open-external-link', (event, url) => {
  shell.openExternal(url);
});

ipcMain.handle('select-file', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: options?.filters || [
      { name: 'Documents', extensions: ['pdf', 'docx', 'pptx', 'txt', 'png', 'jpg', 'jpeg'] }
    ]
  });
  return result.filePaths;
});

ipcMain.handle('get-user-data-path', () => {
  return app.getPath('userData');
});

// Auto-updater events
autoUpdater.on('update-available', (info) => {
  log.info('Update available:', info.version);
  if (mainWindow) {
    mainWindow.webContents.send('update-available', info);
  }
});

autoUpdater.on('update-downloaded', (info) => {
  log.info('Update downloaded:', info.version);
  if (mainWindow) {
    mainWindow.webContents.send('update-downloaded', info);
  }
});

ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});
