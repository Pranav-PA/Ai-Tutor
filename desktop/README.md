# AI Semester Companion - Desktop Application

A standalone desktop application that bundles the AI-powered tutoring system into a one-click install experience. No terminal commands, no Docker, no manual setup required.

## For Users

### Installation

Download the installer for your platform:

| Platform | File | Size |
|----------|------|------|
| Windows | `AI-Semester-Companion-Setup-1.0.0.exe` | ~200MB |
| macOS (Intel) | `AI-Semester-Companion-1.0.0-x64.dmg` | ~200MB |
| macOS (Apple Silicon) | `AI-Semester-Companion-1.0.0-arm64.dmg` | ~200MB |
| Linux | `AI-Semester-Companion-1.0.0-x64.AppImage` | ~200MB |
| Linux (Debian) | `AI-Semester-Companion-1.0.0-x64.deb` | ~200MB |

### First Launch

1. Install and open the application
2. On first launch, choose your AI provider:
   - **Ollama (Free, Local)** - Runs AI models locally on your machine. Requires [Ollama](https://ollama.ai) installed separately.
   - **OpenAI** - Uses GPT-4o (requires API key)
   - **Google Gemini** - Uses Gemini 1.5 Pro (requires API key)
3. Start uploading your study materials and learning!

### Using Ollama (Free Local AI)

1. Download and install [Ollama](https://ollama.ai)
2. Open a terminal and run: `ollama pull llama3.1`
3. In the app settings, select "Ollama" as your provider
4. The app will automatically connect to your local Ollama instance

### Auto-Updates

The app checks for updates automatically and will notify you when a new version is available.

---

## For Developers

### Architecture

```
desktop/
├── electron/           # Electron main process
│   ├── main.js         # App entry point, window management
│   ├── preload.js      # Context bridge (renderer ↔ main)
│   ├── backend-manager.js  # Python backend lifecycle
│   ├── menu.js         # Application menu
│   └── splash.html     # Loading splash screen
├── build/              # Icons and build resources
├── frontend-dist/      # Built Next.js static export (generated)
├── backend-dist/       # PyInstaller backend bundle (generated)
├── package.json        # Electron app config & electron-builder
├── build.sh            # Unix build script
└── build.bat           # Windows build script
```

### How It Works

1. **Electron** creates the desktop window and manages the app lifecycle
2. **Backend Manager** spawns the bundled Python backend as a child process
3. The backend starts on a random available port (localhost only)
4. The frontend loads as a static HTML/JS bundle and connects to the backend API
5. All user data is stored in the OS-specific app data directory

### Development Setup

```bash
# 1. Clone the repo
git clone <repo-url>
cd ai-semester-companion

# 2. Install backend dependencies
cd backend
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt

# 3. Install frontend dependencies
cd ../frontend
npm install

# 4. Install desktop app dependencies
cd ../desktop
npm install

# 5. Start in development mode
# Terminal 1: Backend
cd ../backend && uvicorn backend.main:app --host 127.0.0.1 --port 18080

# Terminal 2: Frontend
cd ../frontend && npm run dev

# Terminal 3: Electron (dev mode connects to running frontend)
cd ../desktop && npm run dev
```

### Building for Distribution

```bash
# Build everything (current platform)
cd desktop
./build.sh

# Build for specific platform
./build.sh --platform win
./build.sh --platform mac
./build.sh --platform linux

# Build for all platforms
./build.sh --all

# Skip steps if already built
./build.sh --skip-backend
./build.sh --skip-frontend
```

### Build Requirements

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **PyInstaller** (installed automatically during build)
- For Windows builds: Windows 10+ or Wine on Linux/macOS
- For macOS builds: macOS with Xcode command line tools
- For Linux builds: Any modern Linux distribution

### Signing & Notarization

For production releases:

- **Windows**: Use a code signing certificate and set `CSC_LINK`/`CSC_KEY_PASSWORD` env vars
- **macOS**: Requires Apple Developer certificate and notarization. Set `APPLE_ID`, `APPLE_APP_SPECIFIC_PASSWORD`, and `APPLE_TEAM_ID` env vars
- **Linux**: No signing required for AppImage/deb

### Release Process

1. Update version in `desktop/package.json`
2. Build for all platforms
3. Create GitHub release and upload artifacts
4. The auto-updater will detect the new version automatically
