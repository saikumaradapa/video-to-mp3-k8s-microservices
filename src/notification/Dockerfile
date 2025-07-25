# Use a slim Python 3.10 image as the base
FROM python:3.10-slim-bullseye

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    # Install compiler tools for Python packages with native extensions
    apt-get install -y --no-install-recommends --no-install-suggests \
        build-essential \
        ffmpeg && \
    # Upgrade pip
    pip install --no-cache-dir --upgrade pip && \
    # Clean up cache and lists to reduce image size
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install dependencies first (layer caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command to run the consumer
CMD ["python3", "consumer.py"]
