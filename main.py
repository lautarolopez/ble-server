from bluezero import peripheral, adapter, async_tools
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}


def read_status():
    """
    Read callback for the status characteristic.
    Returns the current status as a JSON-encoded byte array.
    """
    logger.debug("Status read requested")
    return json.dumps(status).encode()


def write_command(value, options):
    """
    Write callback for the command characteristic.
    Expects commands like 'START' and 'STOP' to change the status.
    """
    global status
    try:
        command = bytes(value).decode().strip().upper()
        logger.debug(f"Command received: {command}")

        if command == 'START':
            status['running'] = True
            logger.info("Status changed to RUNNING")
        elif command == 'STOP':
            status['running'] = False
            logger.info("Status changed to STOPPED")
        else:
            logger.warning(f"Unknown command received: {command}")
            return

        notify_status_change()
    except Exception as e:
        logger.error(f"Error handling command: {e}", exc_info=True)


def notify_status_change(characteristic=None):
    """
    Update the notify characteristic with the current status.
    """
    global status
    try:
        notify_value = json.dumps(status).encode()
        if characteristic and characteristic.is_notifying:
            characteristic.set_value(notify_value)
            logger.info(f"Notification sent: {status}")
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)


def notify_callback(notifying, characteristic):
    """
    Callback for when notifications are enabled or disabled.
    """
    if notifying:
        logger.info("Notifications started")
        notify_status_change(characteristic)
    else:
        logger.info("Notifications stopped")


def main(adapter_address):
    """
    Set up the BLE peripheral.
    """
    try:
        # Log adapter address
        logger.info(f"Using adapter: {adapter_address}")

        # Create peripheral
        periph = peripheral.Peripheral(adapter_address, local_name='StatusServer')

        # Add service
        periph.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)
        logger.info(f"Service added with UUID: {SERVICE_UUID}")

        # Add write characteristic
        periph.add_characteristic(
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
        periph.add_characteristic(
            srv_id=1,
            chr_id=2,
            uuid=CHAR_UUID_NOTIFY,
            value=[],
            notifying=False,
            flags=['notify', 'read'],
            read_callback=read_status,
            notify_callback=notify_callback
        )
        logger.info(f"Notify characteristic added with UUID: {CHAR_UUID_NOTIFY}")

        # Publish and run
        periph.publish()
        logger.info("Peripheral published successfully")
        async_tools.run()
    except Exception as e:
        logger.error(f"Setup error: {e}", exc_info=True)


if __name__ == '__main__':
    adapters = adapter.list_adapters()
    if not adapters:
        logger.error("No Bluetooth adapters found")
        exit(1)
    main(adapters[0])