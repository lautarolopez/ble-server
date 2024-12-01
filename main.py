from bluezero import peripheral, adapter
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}
notify_char = None  # To store notify characteristic for use later


def notify_status_change():
    """Send notification with the updated status."""
    global notify_char, status
    if notify_char:
        try:
            notify_value = json.dumps(status).encode()
            notify_char.notify(notify_value)
            logger.info(f"Notified status change: {status}")
        except Exception as e:
            logger.error(f"Failed to notify status change: {e}", exc_info=True)
    else:
        logger.warning("Notify characteristic is not defined")


def write_command(value, options):
    global status
    try:
        # Convert list of integers to bytes
        byte_value = bytes(value)
        
        # Decode the byte string
        command = byte_value.decode().strip().upper()
        logger.info(f"Decoded command received: {command}")
        
        if command == 'START':
            status['running'] = True
            logger.info("Status changed to RUNNING")
        elif command == 'STOP':
            status['running'] = False
            logger.info("Status changed to STOPPED")
        else:
            logger.warning(f"Unknown command received: {command}")
            return
        
        # Notify the updated status
        notify_status_change()
    
    except Exception as e:
        logger.error(f"Error in write_command: {e}", exc_info=True)


def read_status():
    """Return the current status."""
    logger.info("Status read requested")
    return json.dumps(status).encode()


# Main setup for the BLE server
try:
    adapters = adapter.list_adapters()
    if not adapters:
        logger.error("No Bluetooth adapters found")
        exit(1)

    # Create peripheral
    periph = peripheral.Peripheral(
        adapter_address=adapters[0], 
        local_name='TestWithPython'
    )
    logger.info(f"Using adapter: {adapters[0]}")

    # Add service
    service = periph.add_service(
        srv_id=1, 
        uuid=SERVICE_UUID, 
        primary=True
    )
    logger.info(f"Service added with UUID: {SERVICE_UUID}")

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
    logger.info(f"Write characteristic added with UUID: {CHAR_UUID_WRITE}")

    # Add notify characteristic
    notify_char = periph.add_characteristic(
        srv_id=1, 
        chr_id=2, 
        uuid=CHAR_UUID_NOTIFY,
        value=[],
        notifying=True,
        flags=['notify', 'read'],
        read_callback=read_status
    )
    logger.info(f"Notify characteristic added with UUID: {CHAR_UUID_NOTIFY}")

    # Publish the peripheral
    periph.publish()
    logger.info("Peripheral published successfully")

    # Run the main loop
    periph.run()

except Exception as e:
    logger.error(f"Setup error: {e}", exc_info=True)