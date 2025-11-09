# Multi-stage build for optimized image size
# Using CUDA base image for GPU support
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04 as builder

# Install Python 3.12
RUN apt-get update && apt-get install -y \
  software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update && apt-get install -y \
  python3.12 \
  python3.12-dev \
  python3.12-distutils \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

# Set python3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
  build-essential \
  libpq-dev \
  curl \
  git \
  && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  UV_SYSTEM_PYTHON=1 \
  PATH="/app/.venv/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies (including GPU-accelerated packages)
RUN uv pip install --system --no-cache -r pyproject.toml && \
  uv pip install --system --no-cache "uvicorn[standard]" && \
  uv pip install --system --no-cache "unstructured-inference[gpu]"

# Final stage
FROM nvidia/cuda:12.1.0-cudnn8-runtime-ubuntu22.04

# Install Python 3.12
RUN apt-get update && apt-get install -y \
  software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update && apt-get install -y \
  python3.12 \
  python3.12-dev \
  python3-pip \
  && rm -rf /var/lib/apt/lists/*

# Set python3.12 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
  libpq5 \
  curl \
  libgl1 \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  libgomp1 \
  libmagic1 \
  poppler-utils \
  tesseract-ocr \
  libreoffice \
  pandoc \
  && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=/app

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
  chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

