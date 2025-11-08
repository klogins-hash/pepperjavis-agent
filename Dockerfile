FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
COPY requirements-docker.txt .

RUN pip install --no-cache-dir -r requirements.txt -r requirements-docker.txt

# Copy application code
COPY pepperjavis/ ./pepperjavis/
COPY main.py .
COPY pyproject.toml .

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port for API
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "pepperjavis.server:app", "--host", "0.0.0.0", "--port", "8000"]
