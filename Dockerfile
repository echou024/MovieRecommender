FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for IMDbPY (it needs lxml, requests, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit when container starts
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
