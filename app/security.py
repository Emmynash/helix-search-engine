import socket
import ipaddress
import asyncio
from urllib.parse import urlparse
from fastapi import HTTPException

# Senior Dev Logic: Explicitly define forbidden networks to prevent SSRF
# We block Loopback, Private ranges, and Link-Local (cloud metadata).
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
]

async def validate_url_safety(url: str):
    """
    Resolves hostname to IP asynchronously to prevent event loop blocking.
    This protects the main thread from freezing during slow DNS lookups.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid hostname")

        # FIX: Get the running event loop to offload the blocking socket call
        loop = asyncio.get_running_loop()
        try:
            # run_in_executor(None, ...) uses the default ThreadPoolExecutor
            # This allows the blocking gethostbyname to run in a separate thread
            ip_str = await loop.run_in_executor(None, socket.gethostbyname, hostname)
        except socket.gaierror:
            raise HTTPException(status_code=400, detail="Could not resolve hostname")

        ip = ipaddress.ip_address(ip_str)

        # Check against blocked networks
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Access to restricted network ({hostname} -> {ip}) is forbidden."
                )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid URL format")