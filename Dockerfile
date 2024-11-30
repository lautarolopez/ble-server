# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies for Bluetooth
RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    libbluetooth-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install aiobleserver

# Copy the current directory contents into the container
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Expose any necessary ports (BLE uses HCI interface, not TCP ports)
# Expose D-Bus system bus (if needed)
ENV DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket

# Run the application
CMD ["python", "main.py"]