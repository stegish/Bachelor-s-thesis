# File: mcp_server/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the main file
COPY main_simple.py .

# Expose port
EXPOSE 5002

# Run the application directly with Python
CMD ["python", "main_simple.py"]