# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies for Bluetooth, D-Bus, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    python3-dbus \
    build-essential \
    gcc \
    pkg-config \
    python3-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-glib-2.0 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install bluezero

# Set environment variable for D-Bus
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# Copy the current directory contents into the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Run the application
CMD ["python", "main.py"]