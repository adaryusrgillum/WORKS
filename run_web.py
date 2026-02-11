#!/usr/bin/env python3
"""Launcher for the SEOBOT Streamlit app with robust port selection."""

import socket
import subprocess
import sys
from pathlib import Path


def find_free_port(start: int = 8501, attempts: int = 40) -> int:
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError("Could not find an available localhost port for Streamlit.")


def run_command(command: list[str]) -> int:
    try:
        return subprocess.call(command)
    except FileNotFoundError:
        return 127


def main() -> int:
    app_file = Path(__file__).with_name("streamlit_app.py")
    port = find_free_port()
    shared_args = [
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.port",
        str(port),
        "--server.address",
        "127.0.0.1",
        "--server.headless",
        "true",
    ]

    print(f"Starting SEOBOT on http://127.0.0.1:{port}")

    candidates = [
        ["py", "-3.13", *shared_args],
        ["py", "-3", *shared_args],
        [sys.executable, *shared_args],
    ]

    for command in candidates:
        code = run_command(command)
        if code != 127:
            return code

    print("Failed to launch Streamlit. Install it with: py -3.13 -m pip install streamlit")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
