FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for OpenCV & TensorFlow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libgl1 \
        libglib2.0-0 \
        pkg-config \
        wget \
        unzip \
        git \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run sets the PORT environment variable
ENV PORT=8080

CMD exec gunicorn -w 4 -b :$PORT run:app
