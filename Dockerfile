###############################################################################
# AI Semester Companion - Single Dockerfile (multi-stage)
# Builds both backend (Python/FastAPI) and frontend (Next.js) in one image.
# No external DB required — uses SQLite + ChromaDB locally.
###############################################################################

# ═══════════════════════════════════════════════════════════════════════════════
# Stage 1: Frontend build
# ═══════════════════════════════════════════════════════════════════════════════
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci || npm install

# Copy frontend source and build
COPY frontend/ ./

# Set the API URL for the build (proxied via next.config.js rewrites)
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ═══════════════════════════════════════════════════════════════════════════════
# Stage 2: Final runtime image
# ═══════════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

# System dependencies for tesseract OCR, image processing, and node
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    curl \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ─── Python dependencies ─────────────────────────────────────────────────────
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ─── Copy backend source ─────────────────────────────────────────────────────
COPY backend/ ./backend/

# ─── Copy frontend build output ──────────────────────────────────────────────
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/node_modules ./frontend/node_modules
COPY --from=frontend-build /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-build /app/frontend/next.config.js ./frontend/next.config.js

# ─── Create data directory ────────────────────────────────────────────────────
RUN mkdir -p /app/app-data/uploads \
             /app/app-data/vectors \
             /app/app-data/generated \
             /app/app-data/progress \
             /app/app-data/cache \
             /app/app-data/courses

# ─── Supervisor config to run both services ──────────────────────────────────
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# ─── Expose ports ─────────────────────────────────────────────────────────────
# Backend: 18080 | Frontend: 38173
EXPOSE 18080 38173

# ─── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:18080/api/health || exit 1

# ─── Start both services via supervisor ───────────────────────────────────────
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
