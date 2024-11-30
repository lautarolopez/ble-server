# Use a Debian-based Python image
FROM python:3.9-buster

# Install dependencies for Bluetooth, D-Bus, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    build-essential \
    gcc \
    pkg-config \
    python3-dbus \
    python3-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-glib-2.0 \
    && rm -rf /var/lib/apt/lists/*

# Ensure 'python' points to 'python3'
RUN ln -sf /usr/bin/python3 /usr/bin/python

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

# Run the application using 'python3'
CMD ["python", "main.py"]