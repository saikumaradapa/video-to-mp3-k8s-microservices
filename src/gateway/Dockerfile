# Use a slim Python 3.10 image as the base
FROM python:3.10-slim-bullseye

# Update package list, install required system libraries, and upgrade pip
RUN apt-get update \
  # Install essential packages, without optional/suggested extras
  && apt-get install -y --no-install-recommends --no-install-suggests \
  # build-essential: provides tools like gcc, make (used to build Python C extensions)
  build-essential \
  # Upgrade pip with no cache (saves space inside the image)
  && pip install --no-cache-dir --upgrade pip


# Set working directory
WORKDIR /app

# Copy dependency file first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose Flask port
EXPOSE 8080

# Run the Flask application
CMD ["python3", "server.py"]
