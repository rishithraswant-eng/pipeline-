import asyncio
from .base import BaseServiceEmulator

class SMBEmulator(BaseServiceEmulator):
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            if not data:
                return
            
            # Simple dummy NetBIOS + SMB2 Negotiate Protocol Response
            smb2_neg_resp = (
                b'\x00\x00\x00\x41'
                b'\xfeSMB'
                b'\x40\x00'
                b'\x00\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x00'
                b'\x01\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x41\x00'
                b'\x01\x00'
                b'\x00\x00'
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
                b'\x00\x00\x00\x00'
                b'\x00\x10\x00\x00'
                b'\x00\x10\x00\x00'
                b'\x00\x10\x00\x00'
            )
            writer.write(smb2_neg_resp)
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
