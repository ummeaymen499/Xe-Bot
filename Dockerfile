# Production Dockerfile for Xe-Bot Backend
# Works with Render, Railway, Heroku, etc.

FROM python:3.11-slim

# Install system dependencies for Manim and video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools
    gcc \
    g++ \
    pkg-config \
    # Manim dependencies
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libgirepository1.0-dev \
    # TeX for mathematical expressions (minimal)
    texlive-base \
    texlive-latex-base \
    texlive-fonts-recommended \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY server.py .
COPY main.py .

# Create output directories
RUN mkdir -p output/animations/videos output/media/videos cache/papers

# Environment variables for production
ENV PYTHONUNBUFFERED=1 \
    ANIMATION_QUALITY=low_quality \
    ANIMATION_FPS=15 \
    RENDER_TIMEOUT=300

# Expose port (will be overridden by cloud providers)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run the server
CMD ["python", "server.py"]
