# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install OS-level dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ src/
COPY config/ config/
COPY data/ data/

# Create logs directory
RUN mkdir logs

# Set default command
CMD ["python", "src/ingest.py"]
