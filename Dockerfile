# Neurodiversity Support Coach — Railway Dockerfile
# Python 3.12 slim, Flask + Gunicorn

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Railway injects $PORT at runtime — Gunicorn reads it via the shell command
CMD gunicorn web_coach:app \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120