import asyncio
import os
import logging
from typing import Dict, Any

from .services.ssh import SSHEmulator
from .services.http import HTTPEmulator
from .services.smb import SMBEmulator
from .services.ldap import LDAPEmulator
from .services.db import DBEmulator

logger = logging.getLogger(__name__)

class ShadowMeshCore:
    def __init__(self, registry, topology):
        self.registry = registry
        self.topology = topology
        self.demo_mode = os.environ.get("DEMO_MODE", "false").strip().lower() == "true"
        self.running = False
        self.servers = []
        self.packet_count = 0
        
    async def start(self):
        if self.running:
            return
        self.running = True
        self.packet_count = 0
        if self.demo_mode:
            logger.info("Starting ShadowMeshCore in DEMO_MODE (asyncio listeners)")
            ports = {
                22: SSHEmulator,
                80: HTTPEmulator,
                # 443: HTTPEmulator,  # Removed 443 as plain HTTP fails fingerprinting. Requires proper TLS setup.
                445: SMBEmulator,
                389: LDAPEmulator,
                3306: DBEmulator,
                1433: DBEmulator
            }
            # For DEMO_MODE on Windows, we bind to 127.0.0.1 as a fallback for topology IPs
            bind_ip = "127.0.0.1"
            for port, EmulatorClass in ports.items():
                try:
                    emulator = EmulatorClass(port=port, host_ip=bind_ip)
                    server = await asyncio.start_server(
                        self._wrap_handle_connection(emulator.handle_connection),
                        host=bind_ip,
                        port=port,
                        reuse_address=True
                    )
                    self.servers.append(server)
                    logger.info(f"Started listener on port {port}")
                except Exception as e:
                    logger.error(f"Failed to start listener on port {port}: {e}")
        else:
            logger.info("Starting ShadowMeshCore with NFQueue (Linux only)")
            raise NotImplementedError("NFQueue mode not fully implemented yet. Use DEMO_MODE=true on Windows.")

    def _wrap_handle_connection(self, handler):
        async def wrapped(reader, writer):
            self.packet_count += 1
            await handler(reader, writer)
        return wrapped
            
    async def stop(self):
        self.running = False
        for server in self.servers:
            server.close()
            await server.wait_closed()
        self.servers = []
