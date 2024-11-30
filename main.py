import asyncio
from aiobleserver import Server, Service, Characteristic, Descriptor

from aiobleserver import adapters

SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAR_UUID_WRITE = "12345678-1234-5678-1234-56789abcdef1"
CHAR_UUID_NOTIFY = "12345678-1234-5678-1234-56789abcdef2"

status = {"running": False}

class MyBLEServer(Server):
    def __init__(self):
        super().__init__()
        self.add_service(
            Service(
                SERVICE_UUID,
                [
                    Characteristic(
                        CHAR_UUID_WRITE,
                        Characteristic.WRITE,
                        self.on_write,
                    ),
                    Characteristic(
                        CHAR_UUID_NOTIFY,
                        Characteristic.NOTIFY,
                        None,
                        self.on_subscribe,
                    ),
                ],
            )
        )

    async def on_write(self, characteristic, value, notify):
        global status
        command = value.decode().strip().upper()
        if command == "START":
            status["running"] = True
        elif command == "STOP":
            status["running"] = False
        else:
            print(f"Unknown command: {command}")
            return
        # Notify subscribed clients
        data = str(status).encode()
        await characteristic.notify(data)

    async def on_subscribe(self, characteristic, notify_func):
        # Send initial status
        data = str(status).encode()
        await notify_func(data)

async def main():
    adapter = adapters.get_adapter()
    server = MyBLEServer()
    await server.start("TestWithPython", adapter)
    print("BLE server started...")
    await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())