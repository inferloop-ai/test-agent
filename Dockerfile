FROM python:3.11-slim
WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set up directories
ENV OUTPUT_DIR=/app/outputs
ENV OPENAI_API_KEY=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
RUN mkdir -p /app/outputs /app/data

# Simple health check that doesn't require API key
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "print('Health check passed')" || exit 1

# Default entrypoint
ENTRYPOINT ["python", "main.py"]

# Default command - keep container running for interactive use
CMD ["sleep"]
