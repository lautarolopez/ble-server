# your_script_name.py

from bluezero import peripheral
import json

SERVICE_UUID = '12345678-1234-5678-1234-56789abcdef0'
CHAR_UUID_WRITE = '12345678-1234-5678-1234-56789abcdef1'
CHAR_UUID_NOTIFY = '12345678-1234-5678-1234-56789abcdef2'

status = {'running': False}

class MyPeripheral(peripheral.Peripheral):
    def __init__(self):
        super().__init__(adapter_addr=None, local_name='TestWithPython')
        self.add_service(MyService())

class MyService(peripheral.Service):
    def __init__(self):
        super().__init__(SERVICE_UUID)
        self.add_characteristic(WriteCharacteristic(self))
        self.notify_characteristic = NotifyCharacteristic(self)
        self.add_characteristic(self.notify_characteristic)

class WriteCharacteristic(peripheral.Characteristic):
    def __init__(self, service):
        super().__init__(
            service=service,
            uuid=CHAR_UUID_WRITE,
            flags=['write'],
            write_callback=self.on_write
        )

    def on_write(self, value, options):
        global status
        command = value.decode().strip().upper()
        if command == 'START':
            status['running'] = True
        elif command == 'STOP':
            status['running'] = False
        else:
            print(f"Unknown command: {command}")
            return
        # Notify subscribed clients
        data = json.dumps(status)
        self.service.notify_characteristic.send_notify(data.encode())

class NotifyCharacteristic(peripheral.Characteristic):
    def __init__(self, service):
        super().__init__(
            service=service,
            uuid=CHAR_UUID_NOTIFY,
            flags=['notify']
        )
        self.notifying = False

    def send_notify(self, data):
        if self.notifying:
            self.send_notification(data)

    def read_value(self):
        return json.dumps(status).encode()

    def start_notify(self):
        self.notifying = True
        # Send initial status
        self.send_notify(self.read_value())

    def stop_notify(self):
        self.notifying = False

def main():
    my_peripheral = MyPeripheral()
    my_peripheral.run()

if __name__ == '__main__':
    main()