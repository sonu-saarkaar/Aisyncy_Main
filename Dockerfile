# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p /app/templates/admin /app/static /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set permissions
RUN chown -R nobody:nogroup /app
USER nobody

# Expose port
EXPOSE 8080

# Run the application with Gunicorn
CMD exec gunicorn --config gunicorn.conf.py main:app 