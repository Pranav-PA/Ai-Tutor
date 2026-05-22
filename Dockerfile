###############################################################################
# AI Semester Companion - Single Dockerfile (multi-stage)
# Builds both backend (Python/FastAPI) and frontend (Next.js) in one image.
# No external DB required — uses SQLite + ChromaDB locally.
###############################################################################

# ═══════════════════════════════════════════════════════════════════════════════
# Stage 1: Frontend build
# ═══════════════════════════════════════════════════════════════════════════════
FROM node:20-bookworm-slim AS frontend-build

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
# Stage 2: Node runtime artifacts (copied into final image)
# ═══════════════════════════════════════════════════════════════════════════════
FROM node:20-bookworm-slim AS node-runtime

# ═══════════════════════════════════════════════════════════════════════════════
# Stage 3: Final runtime image
# ═══════════════════════════════════════════════════════════════════════════════
FROM python:3.11-slim

WORKDIR /app

# ─── Copy Node runtime (no apt required) ─────────────────────────────────────
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/bin/npm /usr/local/bin/npm
COPY --from=node-runtime /usr/local/bin/npx /usr/local/bin/npx
COPY --from=node-runtime /usr/local/bin/corepack /usr/local/bin/corepack
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules

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

# ─── Expose ports ─────────────────────────────────────────────────────────────
# Backend: 18080 | Frontend: 38173
EXPOSE 18080 38173

# ─── Health check ─────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:18080/api/health', timeout=5)"

# ─── Start script ────────────────────────────────────────────────────────────
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
