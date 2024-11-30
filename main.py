# main.py

from bluezero import peripheral
import json

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}

def write_command(value, options):
    global status
    command = value.decode().strip().upper()
    if command == 'START':
        status['running'] = True
    elif command == 'STOP':
        status['running'] = False
    else:
        print(f"Unknown command: {command}")
        return
    # Notify clients about the status change
    data = json.dumps(status).encode()
    periph.update_characteristic_value(1, 2, data)
    periph.notify(1, 2)

def read_status():
    # Return the current status as JSON-encoded bytes
    return json.dumps(status).encode()

# Create the peripheral
periph = peripheral.Peripheral(adapter_addr=None, local_name='TestWithPython')

# Add service
periph.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

# Add write characteristic
periph.add_characteristic(srv_id=1, chr_id=1, uuid=CHAR_UUID_WRITE,
                          value=[],
                          notifying=False,
                          flags=['write'],
                          write_callback=write_command)

# Add notify characteristic
periph.add_characteristic(srv_id=1, chr_id=2, uuid=CHAR_UUID_NOTIFY,
                          value=[],
                          notifying=False,
                          flags=['notify', 'read'],
                          read_callback=read_status)

# Publish the peripheral
periph.publish()

# Run the main loop
try:
    periph.run()
except KeyboardInterrupt:
    periph.stop()