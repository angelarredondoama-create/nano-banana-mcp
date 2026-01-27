FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY server.py .

# Expose port for HTTP mode
EXPOSE 8000

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Run server in HTTP mode
CMD ["python", "server.py", "--http"]
