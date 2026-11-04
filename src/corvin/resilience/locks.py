"""
Reference-Counted User Lock Registry for Corvin.
Guarantees atomic per-user turn processing with zero lock eviction race conditions
and zero memory leaks.
"""

import contextlib
import threading
from typing import Dict


class _RefCountedLock:
    __slots__ = ("lock", "ref_count")

    def __init__(self):
        self.lock = threading.Lock()
        self.ref_count = 0


class UserLockRegistry:
    """
    Thread-safe, Reference-Counted User Lock Registry.

    Guarantees:
    - Zero Race Conditions: A lock is NEVER evicted or dropped while any thread
      is actively acquiring, holding, or waiting on it.
    - Zero Memory Leaks: Once all threads for a user complete, the user lock
      is automatically pruned from the registry.
    - Minimal Contention: The internal global lock is held only for microsecond
      dictionary lookups/increments, never across turn evaluation or storage writes.
    """

    def __init__(self):
        self._locks: Dict[str, _RefCountedLock] = {}
        self._global_lock = threading.Lock()

    @contextlib.contextmanager
    def acquire(self, user_id: str):
        with self._global_lock:
            ref_lock = self._locks.get(user_id)
            if ref_lock is None:
                ref_lock = _RefCountedLock()
                self._locks[user_id] = ref_lock
            ref_lock.ref_count += 1

        try:
            ref_lock.lock.acquire()
            try:
                yield ref_lock.lock
            finally:
                ref_lock.lock.release()
        finally:
            with self._global_lock:
                ref_lock.ref_count -= 1
                if ref_lock.ref_count <= 0:
                    self._locks.pop(user_id, None)

    def active_user_count(self) -> int:
        """Returns the number of user locks currently tracked in the registry."""
        with self._global_lock:
            return len(self._locks)

    def __len__(self) -> int:
        """Returns the number of user locks currently tracked in the registry."""
        return self.active_user_count()

