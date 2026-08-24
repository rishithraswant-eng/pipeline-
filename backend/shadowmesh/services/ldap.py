import asyncio
from .base import BaseServiceEmulator

class LDAPEmulator(BaseServiceEmulator):
    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=5.0)
            if not data:
                return
            # Dummy LDAP bind response
            ldap_resp = bytes.fromhex("300c02010161070a010004000400")
            writer.write(ldap_resp)
            await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
