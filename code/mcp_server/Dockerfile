FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add FastAPI and uvicorn
RUN pip install fastapi uvicorn

# Copy source code
COPY src/ ./src/
COPY main_simple.py .

# Create non-root user
RUN useradd -m -u 1000 mcpserver && \
    chown -R mcpserver:mcpserver /app
USER mcpserver

# Expose port for REST API
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Run the simplified server
CMD ["python", "main_simple.py"]