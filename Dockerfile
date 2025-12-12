# Xe-Bot Docker Configuration
# Backend-only build for Render deployment

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Manim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    texlive \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

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
