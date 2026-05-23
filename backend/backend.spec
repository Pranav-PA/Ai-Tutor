# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for AI Semester Companion Backend.

This bundles the FastAPI backend into a standalone executable
that can be shipped with the Electron desktop app.
"""
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all submodules that might be dynamically imported
hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'pydantic',
    'sqlalchemy',
    'sqlalchemy.dialects.sqlite',
    'chromadb',
    'chromadb.config',
    'chromadb.api',
    'chromadb.db',
    'chromadb.db.impl',
    'chromadb.db.impl.sqlite',
    'pdfplumber',
    'docx',
    'pptx',
    'PIL',
    'tiktoken',
    'tiktoken_ext',
    'tiktoken_ext.openai_public',
    'openai',
    'google.generativeai',
    'langchain',
    'langchain_openai',
    'langchain_google_genai',
    'httpx',
    'aiofiles',
    'multipart',
    'dotenv',
    'numpy',
    'sqlite3',
    'backend',
    'backend.main',
    'backend.config',
    'backend.database',
    'backend.database.connection',
    'backend.database.models',
    'backend.services',
    'backend.services.ai_provider',
    'backend.routes',
    'backend.routes.courses',
    'backend.routes.documents',
    'backend.routes.chat',
    'backend.routes.quiz',
    'backend.routes.revision',
    'backend.routes.analytics',
    'backend.routes.settings',
    'backend.routes.planner',
    'backend.rag',
    'backend.rag.vector_store',
    'backend.parsers',
    'backend.parsers.document_parser',
    'backend.models',
    'backend.models.schemas',
    'backend.agents',
    'backend.agents.orchestrator',
]

# Collect data files needed at runtime
datas = [
    # Tiktoken encoding files
]

# Try to collect tiktoken data
try:
    datas += collect_data_files('tiktoken_ext')
except Exception:
    pass

try:
    datas += collect_data_files('chromadb')
except Exception:
    pass

a = Analysis(
    ['run_backend.py'],
    pathex=[os.path.dirname(os.path.abspath('__file__'))],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'torch',
        'tensorflow',
        'keras',
        'notebook',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ai-companion-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../desktop/build/icon.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ai-companion-backend',
)
