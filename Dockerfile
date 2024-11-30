# Use Debian Bullseye as the base image
FROM debian:bullseye

# Install dependencies for Bluetooth, D-Bus, build tools, and Python
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    build-essential \
    gcc \
    pkg-config \
    python3 \
    python3-dbus \
    python3-dev \
    python3-bluezero \
    libcairo2-dev \
    libgirepository1.0-dev \
    gir1.2-glib-2.0 \
    gobject-introspection \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Set environment variable for D-Bus
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# Copy the current directory contents into the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Run the application using 'python3'
CMD ["python3", "main.py"]