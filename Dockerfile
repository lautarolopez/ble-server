# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies for Bluetooth and D-Bus
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    python3-dbus \
    && rm -rf /var/lib/apt/lists/*

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