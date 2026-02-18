FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libboost-all-dev \
    occt-misc \
    libocct-foundation-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

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
