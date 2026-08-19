"""
Internet Connectivity Detector
Fast, lightweight check without loading heavy HTTP libraries.
"""

import socket
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.2) -> bool:
    """
    Checks if active internet connection is available by opening a quick socket connection to Google DNS.
    Returns True if online, False otherwise.
    """
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.close()
        return True
    except (socket.timeout, socket.error, OSError):
        return False

if __name__ == "__main__":
    is_online = check_internet_connection()
    print(f"🌐 Internet Connectivity Status: {'ONLINE' if is_online else 'OFFLINE'}")
