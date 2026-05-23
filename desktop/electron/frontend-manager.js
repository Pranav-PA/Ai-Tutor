/**
 * Frontend Process Manager
 * 
 * Handles spawning the Next.js standalone server in production.
 * The standalone build includes its own Node.js server.
 */
const { spawn } = require('child_process');
const path = require('path');
const net = require('net');
const kill = require('tree-kill');

class FrontendManager {
  constructor({ resourcePath, backendPort, log, onStatusUpdate }) {
    this.resourcePath = resourcePath;
    this.backendPort = backendPort;
    this.log = log;
    this.onStatusUpdate = onStatusUpdate || (() => {});
    this.process = null;
    this.port = null;
    this.running = false;
  }

  /**
   * Find an available port
   */
  async findAvailablePort(startPort = 38173) {
    return new Promise((resolve, reject) => {
      const server = net.createServer();
      server.listen(startPort, '127.0.0.1', () => {
        const port = server.address().port;
        server.close(() => resolve(port));
      });
      server.on('error', () => {
        resolve(this.findAvailablePort(startPort + 1));
      });
    });
  }

  /**
   * Wait for the frontend server to become responsive
   */
  async waitForServer(port, maxRetries = 20, interval = 500) {
    for (let i = 0; i < maxRetries; i++) {
      try {
        const response = await fetch(`http://127.0.0.1:${port}/`);
        if (response.ok || response.status === 404) {
          return true;
        }
      } catch (e) {
        // Not ready yet
      }
      this.onStatusUpdate(`Starting frontend... (${i + 1}/${maxRetries})`);
      await new Promise(resolve => setTimeout(resolve, interval));
    }
    throw new Error('Frontend server failed to start within timeout');
  }

  /**
   * Start the Next.js standalone server
   */
  async start() {
    this.onStatusUpdate('Starting frontend server...');
    this.port = await this.findAvailablePort();

    const serverPath = path.join(this.resourcePath, 'frontend', 'server.js');
    
    // Use the bundled Node.js from Electron
    const nodePath = process.execPath;
    
    const env = {
      ...process.env,
      PORT: String(this.port),
      HOSTNAME: '127.0.0.1',
      NODE_ENV: 'production',
      // Tell the frontend where the API backend is
      NEXT_PUBLIC_API_URL: `http://127.0.0.1:${this.backendPort}`,
    };

    this.log.info(`Starting frontend server on port ${this.port}`);
    this.log.info(`Server path: ${serverPath}`);

    this.process = spawn(nodePath, [serverPath], {
      cwd: path.join(this.resourcePath, 'frontend'),
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true
    });

    this.process.stdout.on('data', (data) => {
      const output = data.toString().trim();
      if (output) this.log.info(`[Frontend] ${output}`);
    });

    this.process.stderr.on('data', (data) => {
      const output = data.toString().trim();
      if (output) this.log.warn(`[Frontend:err] ${output}`);
    });

    this.process.on('exit', (code, signal) => {
      this.log.info(`Frontend process exited with code ${code}, signal ${signal}`);
      this.running = false;
      this.process = null;
    });

    this.process.on('error', (err) => {
      this.log.error('Frontend process error:', err);
      this.running = false;
    });

    await this.waitForServer(this.port);
    this.running = true;
    return this.port;
  }

  /**
   * Stop the frontend process
   */
  async stop() {
    if (this.process) {
      this.log.info('Stopping frontend process...');
      return new Promise((resolve) => {
        const pid = this.process.pid;
        kill(pid, 'SIGTERM', (err) => {
          if (err) {
            try { kill(pid, 'SIGKILL'); } catch (e) {}
          }
          this.process = null;
          this.running = false;
          resolve();
        });
        setTimeout(() => {
          if (this.process) {
            try { kill(pid, 'SIGKILL'); } catch (e) {}
            this.process = null;
            this.running = false;
            resolve();
          }
        }, 3000);
      });
    }
  }

  isRunning() { return this.running; }
  getPort() { return this.port; }
}

module.exports = { FrontendManager };
