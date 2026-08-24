"""Start the local FastAPI, MCP, and Streamlit services together."""

import os
import signal
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path

# Make the repository root importable when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config.config import Settings


def start_process(
    command: list[str], environment: dict[str, str]
) -> subprocess.Popen[bytes]:
    """Start one local service and return its process handle."""
    return subprocess.Popen(command, env=environment)


def stop_processes(processes: Iterable[subprocess.Popen[bytes]]) -> None:
    """Stop all child services started by this launcher."""
    for process in processes:
        if process.poll() is None:
            process.send_signal(signal.SIGTERM)
    for process in processes:
        process.wait()


def main() -> None:
    """Run all local application services until interrupted."""
    environment = os.environ.copy()
    settings = Settings()
    environment.setdefault("OPTIONAI_API_URL", settings.api_url)
    environment.setdefault("OPTIONAI_MCP_URL", settings.mcp_url)
    environment.setdefault("OPTIONAI_MCP_PORT", str(settings.mcp_port))
    environment.setdefault(
        "OPTIONAI_TECHNICAL_DATA_PROVIDER", settings.technical_data_provider
    )
    mcp_server_module = (
        "app.mcp.raw_server"
        if settings.technical_data_provider == "raw_mcp"
        else "app.mcp.server"
    )
    commands = [
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.api.main:app",
            "--host",
            settings.api_host,
            "--port",
            str(settings.api_port),
        ],
    ]
    if settings.technical_data_provider != "direct":
        commands.append([sys.executable, "-m", mcp_server_module])
    commands.append([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    processes = [start_process(command, environment) for command in commands]
    try:
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        pass
    finally:
        stop_processes(processes)


if __name__ == "__main__":
    main()
