"""Small standard-library client for the Optipus legacy Data Server API."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any, Mapping
from urllib.parse import quote
from urllib.request import Request, urlopen


class OptipusPeripheral:
    """Read and write scalar nodes and publish peripheral health status."""

    protocol_version = "1.0"

    def __init__(
        self,
        host: str,
        port: int,
        peripheral_id: str,
        name: str,
        request_interval: float = 5.0,
        heartbeat_interval: float = 15.0,
        timeout: float = 3.0,
    ) -> None:
        if not peripheral_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_." for char in peripheral_id):
            raise ValueError("peripheral_id may contain only letters, numbers, '-', '_' and '.'")
        if request_interval <= 0 or heartbeat_interval <= 0 or timeout <= 0:
            raise ValueError("intervals and timeout must be greater than zero")

        self.base_url = f"http://{host}:{port}"
        self.peripheral_id = peripheral_id
        self.name = name
        self.request_interval = request_interval
        self.heartbeat_interval = heartbeat_interval
        self.timeout = timeout
        self._request_count = 0
        self._error_code = 0
        self._last_heartbeat = 0.0

    @property
    def root(self) -> str:
        return "peripheral"

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _get_json(self, path: str) -> Any:
        request = Request(f"{self.base_url}/list/{quote(path, safe='.')}", method="GET")
        with urlopen(request, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _set_value(self, path: str, value: Any) -> None:
        if isinstance(value, bool):
            encoded_value = "true" if value else "false"
        elif value is None:
            encoded_value = "None"
        elif isinstance(value, (str, int, float)):
            encoded_value = str(value) or "None"
        else:
            raise TypeError("The legacy API supports scalar values only")

        request = Request(
            f"{self.base_url}/set/{quote(path, safe='.')}/{quote(encoded_value, safe='')}",
            method="GET",
        )
        with urlopen(request, timeout=self.timeout):
            return

    def read(self, node: str) -> Any:
        return self._get_json(f"{self.root}.values.{node}")

    def write(self, node: str, value: Any) -> None:
        self._set_value(f"{self.root}.values.{node}", value)

    def setErrorCode(self, code: int) -> None:
        """Publish a non-zero application error code."""
        if isinstance(code, bool) or not isinstance(code, int) or code < 0:
            raise ValueError("error code must be a positive integer")
        self._error_code = code
        self._set_value(f"{self.root}.status.errorFlag", code)

    def resetError(self) -> None:
        """Clear the application error flag."""
        self._error_code = 0
        self._set_value(f"{self.root}.status.errorFlag", 0)

    def heartbeat(self, online: bool = True, error: str = "") -> None:
        now = self._timestamp()
        status = {
            "online": online,
            "lastRequestTimestamp": now,
            "lastSuccessTimestamp": now if online else "",
            "lastError": error or "No error",
            "errorFlag": self._error_code,
            "requestCount": self._request_count,
        }
        self._set_value(f"{self.root}.meta.name", self.name)
        self._set_value(f"{self.root}.meta.platform", "python")
        self._set_value(f"{self.root}.meta.protocolVersion", self.protocol_version)
        for node, value in status.items():
            self._set_value(f"{self.root}.status.{node}", value)
        self._last_heartbeat = time.monotonic()

    def run_once(self, inputs: Mapping[str, str], outputs: Mapping[str, Any]) -> dict[str, Any]:
        """Read inputs, write outputs, and update status once."""
        try:
            values = {name: self.read(node) for name, node in inputs.items()}
            for node, value in outputs.items():
                self.write(node, value)
            self._request_count += 1
            if time.monotonic() - self._last_heartbeat >= self.heartbeat_interval:
                self.heartbeat()
            return values
        except OSError as error:
            if self._error_code == 0:
                self._error_code = 1
            self.heartbeat(online=False, error=str(error))
            raise
