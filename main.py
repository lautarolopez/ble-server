from bluezero import peripheral, adapter
import json
import logging

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}

def write_command(characteristic, value):
    global status
    try:
        # Log the received raw value
        logger.info(f"Received raw value: {value}")
        
        command = value.decode().strip().upper()
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
        
        # Convert status to bytes
        status_bytes = json.dumps(status).encode()
        logger.debug(f"Prepared notification payload: {status_bytes}")
        
        # Update characteristic value
        characteristic.value = list(status_bytes)
        
        # Log before notification attempt
        logger.info("Attempting to start notification")
        
        # Explicitly start notification
        if hasattr(characteristic, 'StartNotify'):
            try:
                characteristic.StartNotify()
                logger.info("Notification started successfully")
            except Exception as notify_error:
                logger.error(f"Failed to start notification: {notify_error}")
        else:
            logger.warning("StartNotify method not available")
        
    except Exception as e:
        logger.error(f"Error in write_command: {e}", exc_info=True)

def read_status():
    logger.info("Status read requested")
    return json.dumps(status).encode()

# Get adapter
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

    periph.publish()
    logger.info("Peripheral published successfully")

    # Run main loop
    periph.run()

except Exception as e:
    logger.error(f"Setup error: {e}", exc_info=True)