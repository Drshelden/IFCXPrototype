# Build context is the REPO ROOT (see server/deploy/docker-compose.yml,
# `context: ../..`), not server/, so this stage can reach the top-level
# client/ (Vite) project which lives outside server/.
FROM node:20-slim AS client-build
WORKDIR /client
COPY client/package*.json ./
RUN npm install
COPY client/ ./
RUN npm run build

FROM python:3.11-slim

# /app mirrors this repo's server/ directory (contents copied directly into
# it below) so every path server.py already resolves relative to its own
# file (os.path.dirname(__file__)) keeps working unchanged; /client is
# /app's sibling here exactly as client/ is server/'s sibling in the repo.
WORKDIR /app

# Install system dependencies, including Node.js (needed at RUNTIME, not
# just build time: server/viewer_sidecar_manager.py spawns a Node process
# per model to run ifclite's own viewer server).
RUN apt-get update && apt-get install -y \
    build-essential \
    libboost-all-dev \
    occt-misc \
    libocct-foundation-dev \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./

# Install the viewer sidecar's own Node dependencies (@ifc-lite/viewer-core)
RUN npm --prefix viewer_sidecar install --omit=dev

# Bring in the pre-built client from the first stage
COPY --from=client-build /client/dist /client/dist

# Create directories for uploads and data
RUN mkdir -p uploads dataStores/fileBased/data

# Expose port (Heroku will dynamically assign)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=server.py
ENV PYTHONUNBUFFERED=1

# Run the server
# The PORT environment variable is set by Heroku
CMD exec python server.py \
    --backend ${BACKEND:-fileBased} \
    --host 0.0.0.0 \
    --port ${PORT:-5000}
