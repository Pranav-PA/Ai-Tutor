/**
 * Backend Process Manager
 * 
 * Handles spawning, monitoring, and stopping the Python backend process.
 * In production, uses the PyInstaller-bundled executable.
 * In development, runs the Python script directly.
 */
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const net = require('net');
const kill = require('tree-kill');

class BackendManager {
  constructor({ isDev, resourcePath, userDataPath, store, log, onStatusUpdate }) {
    this.isDev = isDev;
    this.resourcePath = resourcePath;
    this.userDataPath = userDataPath;
    this.store = store;
    this.log = log;
    this.onStatusUpdate = onStatusUpdate || (() => {});
    this.process = null;
    this.port = null;
    this.running = false;
  }

  /**
   * Find an available port
   */
  async findAvailablePort(startPort = 18080) {
    return new Promise((resolve, reject) => {
      const server = net.createServer();
      server.listen(startPort, '127.0.0.1', () => {
        const port = server.address().port;
        server.close(() => resolve(port));
      });
      server.on('error', () => {
        // Port in use, try next
        resolve(this.findAvailablePort(startPort + 1));
      });
    });
  }

  /**
   * Get the path to the backend executable/script
   */
  getBackendPath() {
    if (this.isDev) {
      // In development, run Python directly
      return {
        command: process.platform === 'win32' ? 'python' : 'python3',
        args: ['-m', 'uvicorn', 'backend.main:app', '--host', '127.0.0.1'],
        cwd: path.join(this.resourcePath)
      };
    }

    // In production, use the PyInstaller bundle
    const platform = process.platform;
    let execName = 'ai-companion-backend';
    
    if (platform === 'win32') {
      execName += '.exe';
    }

    const execPath = path.join(this.resourcePath, 'backend', execName);
    
    if (!fs.existsSync(execPath)) {
      throw new Error(`Backend executable not found at: ${execPath}`);
    }

    return {
      command: execPath,
      args: [],
      cwd: path.join(this.resourcePath, 'backend')
    };
  }

  /**
   * Build environment variables for the backend
   */
  getEnvironment() {
    const env = { ...process.env };
    
    // Set data directory to user data path
    env.APP_DATA_DIR = path.join(this.userDataPath, 'app-data');
    env.HOST = '127.0.0.1';
    env.PORT = String(this.port);
    env.DESKTOP_MODE = 'true';
    
    // AI provider settings from store
    const provider = this.store.get('aiProvider');
    env.AI_PROVIDER = provider;
    env.DEFAULT_PROVIDER = provider;
    
    if (this.store.get('openaiApiKey')) {
      env.OPENAI_API_KEY = this.store.get('openaiApiKey');
    }
    if (this.store.get('geminiApiKey')) {
      env.GEMINI_API_KEY = this.store.get('geminiApiKey');
    }
    
    // Ollama settings
    env.OLLAMA_BASE_URL = this.store.get('ollamaUrl') || 'http://localhost:11434';
    env.OLLAMA_MODEL = this.store.get('ollamaModel') || 'llama3.1';
    
    // Disable telemetry
    env.ANONYMIZED_TELEMETRY = 'false';
    
    return env;
  }

  /**
   * Wait for the backend to become responsive
   */
  async waitForBackend(port, maxRetries = 30, interval = 1000) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`http://127.0.0.1:${port}/`);
        if (response.ok) {
          return true;
        }
      } catch (e) {
        // Not ready yet
      }
      this.onStatusUpdate(`Starting services... (${i + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    throw new Error('Backend failed to start within the timeout period');
  }

  /**
   * Start the backend process
   */
  async start() {
    this.onStatusUpdate('Finding available port...');
    this.port = await this.findAvailablePort();
    this.log.info(`Using port ${this.port} for backend`);

    this.onStatusUpdate('Preparing backend...');
    const { command, args, cwd } = this.getBackendPath();
    
    // Add port to args for dev mode
    if (this.isDev) {
      args.push('--port', String(this.port));
    }

    const env = this.getEnvironment();

    this.log.info(`Starting backend: ${command} ${args.join(' ')}`);
    this.log.info(`Working directory: ${cwd}`);

    this.onStatusUpdate('Starting AI engine...');

    this.process = spawn(command, args, {
      cwd,
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true
    });

    // Capture stdout
    this.process.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        this.log.info(`[Backend] ${output}`);
      }
    });

    // Capture stderr
    this.process.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output) {
        this.log.warn(`[Backend:err] ${output}`);
      }
    });

    // Handle exit
    this.process.on('exit', (code, signal) => {
      this.log.info(`Backend process exited with code ${code}, signal ${signal}`);
      this.running = false;
      this.process = null;
    });

    this.process.on('error', (err) => {
      this.log.error('Backend process error:', err);
      this.running = false;
    });

    // Wait for backend to be ready
    this.onStatusUpdate('Waiting for AI engine to initialize...');
    await this.waitForBackend(this.port);
    
    this.running = true;
    this.onStatusUpdate('Ready!');
    return this.port;
  }

  /**
   * Stop the backend process
   */
  async stop() {
    if (this.process) {
      this.log.info('Stopping backend process...');
      return new Promise((resolve) => {
        const pid = this.process.pid;
        
        // Use tree-kill to kill the process and all children
        kill(pid, 'SIGTERM', (err) => {
          if (err) {
            this.log.warn('Error killing backend process:', err);
            // Force kill
            try {
              kill(pid, 'SIGKILL');
            } catch (e) {
              // Already dead
            }
          }
          this.process = null;
          this.running = false;
          resolve();
        });

        // Force kill after timeout
        setTimeout(() => {
          if (this.process) {
            try {
              kill(pid, 'SIGKILL');
            } catch (e) {
              // Already dead
            }
            this.process = null;
            this.running = false;
            resolve();
          }
        }, 5000);
      });
    }
  }

  /**
   * Restart the backend process
   */
  async restart() {
    await this.stop();
    return await this.start();
  }

  /**
   * Update settings (notify running backend)
   */
  async updateSettings(store) {
    if (!this.running || !this.port) return;
    
    try {
      const settings = {
        preferred_provider: store.get('aiProvider'),
        openai_api_key: store.get('openaiApiKey'),
        gemini_api_key: store.get('geminiApiKey'),
        ollama_base_url: store.get('ollamaUrl'),
        ollama_model: store.get('ollamaModel')
      };

      await fetch(`http://127.0.0.1:${this.port}/api/settings`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });
    } catch (e) {
      this.log.warn('Failed to update backend settings:', e.message);
    }
  }

  isRunning() {
    return this.running;
  }

  getPort() {
    return this.port;
  }
}

module.exports = { BackendManager };
