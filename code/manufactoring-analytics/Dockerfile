FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create output directory
RUN mkdir -p /app/analytics_output

# Create non-root user for security
RUN useradd -m -u 1000 analytics && \
    chown -R analytics:analytics /app
USER analytics

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app/src
ENV FLASK_APP=microservice_scheduler.py

# Run the application
CMD ["python", "src/microservice_scheduler.py"]