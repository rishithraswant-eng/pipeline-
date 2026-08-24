import asyncio
from .base import BaseServiceEmulator

class SSHEmulator(BaseServiceEmulator):
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        banner = b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n"
        writer.write(banner)
        await writer.drain()
        try:
            await asyncio.wait_for(reader.read(1024), timeout=5.0)
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
