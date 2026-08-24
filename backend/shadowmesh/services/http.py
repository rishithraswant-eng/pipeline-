import asyncio
from .base import BaseServiceEmulator

class HTTPEmulator(BaseServiceEmulator):
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            request = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), timeout=5.0)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Server: Apache/2.4.41 (Ubuntu)\r\n"
                "Content-Type: text/html\r\n"
                "Connection: close\r\n\r\n"
                "<html><body><h1>It works!</h1></body></html>\n"
            )
            writer.write(response.encode())
            await writer.drain()
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionResetError):
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
