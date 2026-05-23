"""
Entry point for the PyInstaller-bundled backend.
This script starts the FastAPI server as a standalone process.
"""
import os
import sys
import multiprocessing

# Fix for PyInstaller multiprocessing
multiprocessing.freeze_support()

# Set up paths for bundled mode
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    bundle_dir = os.path.dirname(sys.executable)
    sys.path.insert(0, bundle_dir)
    
    # Set the data directory from environment or default
    if not os.environ.get('APP_DATA_DIR'):
        if sys.platform == 'win32':
            app_data = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'AI Semester Companion', 'app-data')
        elif sys.platform == 'darwin':
            app_data = os.path.join(os.path.expanduser('~/Library/Application Support'), 'AI Semester Companion', 'app-data')
        else:
            app_data = os.path.join(os.path.expanduser('~/.config'), 'ai-semester-companion', 'app-data')
        os.environ['APP_DATA_DIR'] = app_data
else:
    # Running in development
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Ensure data directories exist
app_data_dir = os.environ.get('APP_DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'app-data'))
for subdir in ['uploads', 'vectors', 'generated', 'progress', 'cache', 'courses']:
    os.makedirs(os.path.join(app_data_dir, subdir), exist_ok=True)


def main():
    """Start the backend server."""
    import uvicorn
    
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', '18080'))
    
    print(f"Starting AI Semester Companion Backend on {host}:{port}")
    print(f"Data directory: {app_data_dir}")
    
    uvicorn.run(
        'backend.main:app',
        host=host,
        port=port,
        log_level='info',
        workers=1,
        access_log=False
    )


if __name__ == '__main__':
    main()
