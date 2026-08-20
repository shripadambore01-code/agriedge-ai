import os
import socket
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 1.0) -> bool:
    """
    Checks if active internet connection is available.
    Uses socket.create_connection to avoid mutating global socket defaults.
    """
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        return True
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

if __name__ == "__main__":
    is_online = check_internet_connection()
    print(f"🌐 Internet Connectivity Status: {'ONLINE' if is_online else 'OFFLINE'}")

