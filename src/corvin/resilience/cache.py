import threading
import time
from collections import OrderedDict
from typing import TypeVar, Generic, Optional, Any

K = TypeVar("K")
V = TypeVar("V")

class BoundedTTLCache(Generic[K, V]):
    """
    Thread-safe, Bounded LRU Cache with Time-To-Live (TTL) Eviction.
    
    Guarantees:
    - Zero Memory Leaks: Cache size never exceeds `max_size`.
    - Automatic Eviction: Expired keys are discarded automatically upon access or insertion.
    - Thread-Safe: Protected by an RLock for concurrent multi-threaded execution.
    """

    def __init__(self, max_size: int = 10000, ttl_seconds: float = 3600.0):
        if max_size <= 0:
            raise ValueError("max_size must be strictly positive.")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be strictly positive.")

        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._lock = threading.RLock()
        # OrderedDict stores key -> (value, expiry_timestamp)
        self._cache: OrderedDict[K, tuple[V, float]] = OrderedDict()

    def _purge_expired_locked(self, now: float) -> None:
        """Removes expired items from the cache head."""
        expired_keys = [k for k, (v, exp) in self._cache.items() if now >= exp]
        for k in expired_keys:
            del self._cache[k]

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        now = time.time()
        with self._lock:
            if key not in self._cache:
                return default

            value, expiry = self._cache[key]
            if now >= expiry:
                del self._cache[key]
                return default

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return value

    def set(self, key: K, value: V, ttl: Optional[float] = None) -> None:
        now = time.time()
        expiry = now + (ttl if ttl is not None else self.ttl_seconds)

        with self._lock:
            # If key already exists, overwrite and move to end
            if key in self._cache:
                self._cache[key] = (value, expiry)
                self._cache.move_to_end(key)
                return

            # Purge expired items if reaching capacity
            if len(self._cache) >= self.max_size:
                self._purge_expired_locked(now)

            # If still at capacity after purging, evict least recently used (first item)
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)

            self._cache[key] = (value, expiry)

    def __contains__(self, key: K) -> bool:
        return self.get(key) is not None

    def __getitem__(self, key: K) -> V:
        val = self.get(key)
        if val is None:
            raise KeyError(key)
        return val

    def __setitem__(self, key: K, value: V) -> None:
        self.set(key, value)

    def __len__(self) -> int:
        now = time.time()
        with self._lock:
            self._purge_expired_locked(now)
            return len(self._cache)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

