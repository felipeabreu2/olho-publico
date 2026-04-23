from __future__ import annotations

import threading
import time


class TokenBucket:
    """Token bucket simples, thread-safe.

    Usado para respeitar os 90 req/min do Portal da Transparência.
    """

    def __init__(self, *, rate_per_minute: float, capacity: int | None = None):
        self.rate_per_second = rate_per_minute / 60.0
        self.capacity = capacity if capacity is not None else max(1, int(rate_per_minute))
        self._tokens = float(self.capacity)
        self._last_refill = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.capacity, self._tokens + elapsed * self.rate_per_second)
        self._last_refill = now

    def try_acquire(self, n: int = 1) -> bool:
        with self._lock:
            self._refill()
            if self._tokens >= n:
                self._tokens -= n
                return True
            return False

    def acquire(self, n: int = 1) -> None:
        """Bloqueia até ter tokens suficientes."""
        while True:
            if self.try_acquire(n):
                return
            with self._lock:
                deficit = n - self._tokens
                wait = deficit / self.rate_per_second
            time.sleep(max(0.001, wait))
