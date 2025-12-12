# Xe-Bot Docker Configuration
# Backend-only build for Render deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Manim and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools for pycairo/manimpango
    gcc \
    g++ \
    pkg-config \
    # Manim dependencies
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    libgirepository1.0-dev \
    # TeX for mathematical expressions
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    # Utilities
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY server.py .
COPY main.py .
COPY mcp_server.py .

# Create output directories
RUN mkdir -p output/animations/videos output/media/videos cache/papers

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run server
CMD ["python", "server.py"]
