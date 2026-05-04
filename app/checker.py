import socket, subprocess, time
from dataclasses import dataclass

@dataclass
class CheckResult:
    host: str
    port: int | None
    reachable: bool
    latency_ms: float | None
    error: str | None


def check_port(host: str, port: int, timeout: float = 3.0) -> CheckResult:
    start = time.monotonic()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            ms = round((time.monotonic() - start) * 1000, 2)
            return CheckResult(host, port, True,  ms,   None)
    except Exception as e:
        return CheckResult(host, port, False, None, str(e))


def check_ping(host: str) -> CheckResult:
    start = time.monotonic()
    try:
        r = subprocess.run(
            ["ping", "-c", "1", "-W", "3", host],
            capture_output=True, timeout=5
        )
        ms = round((time.monotonic() - start) * 1000, 2)
        if r.returncode == 0:
            return CheckResult(host, None, True,  ms,   None)
        return CheckResult(host, None, False, None, "ping failed")
    except Exception as e:
        return CheckResult(host, None, False, None, str(e))
