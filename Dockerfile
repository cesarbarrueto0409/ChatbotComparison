FROM python:3.14-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Create a non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

# Use uvicorn with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]
