import asyncio
from .base import BaseServiceEmulator

class DBEmulator(BaseServiceEmulator):
    def __init__(self, port: int, host_ip: str = "127.0.0.1"):
        super().__init__(port, host_ip)
        self.db_type = "mysql" if port == 3306 else "mssql"

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            if self.db_type == "mysql":
                # MySQL Initial Handshake Packet
                banner = bytes.fromhex("4a0000000a382e302e333500080000003f3f3f3f3f3f3f3f00ffff080200ff8115000000000000000000003f3f3f3f3f3f3f3f3f3f3f3f006d7973716c5f6e61746976655f70617373776f726400")
                writer.write(banner)
                await writer.drain()
                await asyncio.wait_for(reader.read(1024), timeout=2.0)
            elif self.db_type == "mssql":
                data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
                if data:
                    writer.write(bytes.fromhex("0401002500000100000015000601001b000102001c000103001d0000ff"))
                    await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
