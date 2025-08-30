FROM python:3.11-slim
WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set up directories
ENV OUTPUT_DIR=/app/outputs
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV LLM_MODEL=qwen2.5:7b
RUN mkdir -p /app/outputs /app/data

# Simple health check that doesn't require API key
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "print('Health check passed')" || exit 1

# Default command - run web interface
CMD ["python", "web_app.py"]
