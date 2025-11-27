import socket
import ipaddress
from urllib.parse import urlparse
from fastapi import HTTPException

# Senior Dev Logic: Explicitly define forbidden networks to prevent SSRF
# We block Loopback (127.0.0.0/8), Private ranges (10., 172.16., 192.168.),
# and Link-Local (169.254. - critical for cloud metadata protection).
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
]

def validate_url_safety(url: str):
    """
    Resolves the hostname to an IP and verifies it is not internal.
    Prevents SSRF attacks.
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise ValueError("Invalid hostname")

        # Resolve DNS
        # Note: In production, use an async DNS resolver (like aiodns) to avoid blocking the event loop
        try:
            ip_str = socket.gethostbyname(hostname)
        except socket.gaierror:
            raise HTTPException(status_code=400, detail="Could not resolve hostname")

        ip = ipaddress.ip_address(ip_str)

        # Check if the resolved IP belongs to a blocked network
        for network in BLOCKED_NETWORKS:
            if ip in network:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Access to restricted network ({hostname} -> {ip}) is forbidden."
                )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid URL format")