from bluezero import peripheral, adapter
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}
notify_characteristic = None

def write_command(value, options):
    global status, notify_characteristic
    try:
        command = value.decode().strip().upper()
        logger.info(f"Received command: {command}")
        
        if command == 'START':
            status['running'] = True
        elif command == 'STOP':
            status['running'] = False
        else:
            logger.warning(f"Unknown command: {command}")
            return
        
        # Prepare status as bytes
        status_bytes = json.dumps(status).encode()
        
        # Use the characteristic directly if available
        if notify_characteristic:
            try:
                notify_characteristic.value = list(status_bytes)
                notify_characteristic.notify()
                logger.info("Notification sent successfully")
            except Exception as notify_error:
                logger.error(f"Notification error: {notify_error}")
        else:
            logger.error("Notify characteristic not initialized")
        
    except Exception as e:
        logger.error(f"Error processing command: {e}")

def read_status():
    # Return the current status as JSON-encoded bytes
    return json.dumps(status).encode()

# Get the default adapter's address
adapters = adapter.list_adapters()
if not adapters:
    logger.error("No Bluetooth adapters found")
    exit(1)

adapter_address = adapters[0]
logger.info(f"Using adapter: {adapter_address}")

# Create the peripheral
try:
    periph = peripheral.Peripheral(adapter_address=adapter_address, local_name='TestWithPython')

    # Add service
    service = periph.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)

    # Add write characteristic
    write_char = periph.add_characteristic(
        srv_id=1, 
        chr_id=1, 
        uuid=CHAR_UUID_WRITE,
        value=[],
        notifying=False,
        flags=['write'],
        write_callback=write_command
    )

    # Add notify characteristic
    notify_characteristic = periph.add_characteristic(
        srv_id=1, 
        chr_id=2, 
        uuid=CHAR_UUID_NOTIFY,
        value=[],
        notifying=True,  # Ensure this is set to True
        flags=['notify', 'read'],
        read_callback=read_status
    )

    # Publish the peripheral
    periph.publish()
    logger.info("Peripheral published successfully")

    # Run the main loop
    try:
        periph.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        periph.stop()

except Exception as e:
    logger.error(f"Error setting up peripheral: {e}")