import asyncio

class BaseServiceEmulator:
    def __init__(self, port: int, host_ip: str = "127.0.0.1"):
        self.port = port
        self.host_ip = host_ip
        
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        raise NotImplementedError("Subclasses must implement handle_connection")
