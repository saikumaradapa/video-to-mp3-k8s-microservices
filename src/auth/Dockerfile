# Use a slim Python 3.10 image as the base
FROM python:3.10-slim-bullseye

# Environment settings
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Update packages and install only required system libraries
RUN apt-get update && \
    # Tools like gcc/make (needed for compiling extensions)
    apt-get install -y --no-install-recommends --no-install-suggests build-essential && \
    # MySQL client libraries for Python bindings
    apt-get install -y default-libmysqlclient-dev && \
    # Helps compilers locate libraries
    apt-get install -y pkg-config && \
    # Upgrade pip to latest version
    pip install --no-cache-dir --upgrade pip && \
    # Clean up apt cache to reduce image size
    apt-get clean && \
    # Remove package lists to reduce image size
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency file first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all app files
COPY . .

# Expose the port configured via .env (fallback 5000)
EXPOSE 5000

# Run the Flask app
CMD ["python3", "server.py"]
