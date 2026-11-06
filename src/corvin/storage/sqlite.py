import os
import random
import sqlite3
import time
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Callable

from .base import BaseLedger
from ..core.models import UserPatienceProfile
from ..core.standing import Standing

def with_sqlite_retry(max_retries: int = 5, base_delay: float = 0.05):
    """
    Decorator executing SQLite operations with exponential jittered backoff
    to guarantee resilience against concurrent database locks (SQLITE_BUSY / locked).
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except sqlite3.OperationalError as e:
                    last_err = e
                    if "locked" in str(e).lower() or "busy" in str(e).lower():
                        jitter = random.uniform(0.5, 1.5)
                        sleep_time = (base_delay * (2 ** attempt)) * jitter
                        time.sleep(sleep_time)
                    else:
                        raise
            raise last_err or sqlite3.OperationalError("Database lock retry exhausted.")
        return wrapper
    return decorator


class SQLiteLedger(BaseLedger):
    """
    Hardened SQLite storage engine for The Ledger of Muninn.
    
    Features:
    - High-concurrency WAL mode (Write-Ahead Logging).
    - PRAGMA busy_timeout = 5000ms.
    - Atomic transaction locking (BEGIN IMMEDIATE) to eliminate read-modify-write race conditions.
    - Automatic exponential jittered retries on busy locks.
    """

    def __init__(
        self,
        db_path: str = "ravens_ledger.db",
        busy_timeout_ms: int = 5000,
        max_history_per_user: int = 100,
    ):
        self.db_path = db_path
        self.busy_timeout_ms = busy_timeout_ms
        self.max_history_per_user = max_history_per_user
        parent_dir = os.path.dirname(db_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=self.busy_timeout_ms / 1000.0)
        conn.row_factory = sqlite3.Row
        try:
            # Set high busy_timeout pragma
            conn.execute(f"PRAGMA busy_timeout = {self.busy_timeout_ms};")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raven_profiles (
                    user_id TEXT PRIMARY KEY,
                    patience REAL NOT NULL DEFAULT 100.0,
                    standing TEXT NOT NULL DEFAULT 'GOOD',
                    infraction_count INTEGER NOT NULL DEFAULT 0,
                    last_interaction_ts REAL NOT NULL,
                    created_at_ts REAL NOT NULL,
                    strike_count INTEGER NOT NULL DEFAULT 0,
                    cooldown_until_ts REAL NOT NULL DEFAULT 0.0,
                    consecutive_civil_turns INTEGER NOT NULL DEFAULT 0
                );
            """)
            # Check for existing table schema migrations
            cursor = conn.execute("PRAGMA table_info(raven_profiles);")
            columns = {row["name"] for row in cursor.fetchall()}
            if "strike_count" not in columns:
                conn.execute("ALTER TABLE raven_profiles ADD COLUMN strike_count INTEGER NOT NULL DEFAULT 0;")
            if "cooldown_until_ts" not in columns:
                conn.execute("ALTER TABLE raven_profiles ADD COLUMN cooldown_until_ts REAL NOT NULL DEFAULT 0.0;")
            if "consecutive_civil_turns" not in columns:
                conn.execute("ALTER TABLE raven_profiles ADD COLUMN consecutive_civil_turns INTEGER NOT NULL DEFAULT 0;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS raven_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    stimulus REAL NOT NULL,
                    resulting_patience REAL NOT NULL,
                    posture TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES raven_profiles(user_id)
                );
            """)
            # Explicit indexes for sub-millisecond querying and zero full-table-scan DoS
            conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON raven_interactions(user_id, id DESC);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON raven_interactions(timestamp);")

    @with_sqlite_retry()
    def get_or_create_profile(
        self,
        user_id: str,
        apply_decay: bool = True,
        current_ts: Optional[float] = None,
        half_life_seconds: float = 3600.0,
    ) -> UserPatienceProfile:
        if current_ts is None:
            current_ts = time.time()

        with self._get_connection() as conn:
            # Acquire immediate write lock to prevent race conditions during read-modify-write
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                "SELECT * FROM raven_profiles WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row is None:
                profile = UserPatienceProfile(
                    user_id=user_id,
                    patience=100.0,
                    standing=Standing.GOOD,
                    infraction_count=0,
                    last_interaction_ts=current_ts,
                    created_at_ts=current_ts,
                    strike_count=0,
                    cooldown_until_ts=0.0,
                    consecutive_civil_turns=0,
                )
                conn.execute(
                    """
                    INSERT INTO raven_profiles (
                        user_id, patience, standing, infraction_count,
                        last_interaction_ts, created_at_ts, strike_count, cooldown_until_ts,
                        consecutive_civil_turns
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        profile.user_id,
                        profile.patience,
                        profile.standing.value,
                        profile.infraction_count,
                        profile.last_interaction_ts,
                        profile.created_at_ts,
                        profile.strike_count,
                        profile.cooldown_until_ts,
                        profile.consecutive_civil_turns,
                    )
                )
                return profile

            row_keys = row.keys() if hasattr(row, "keys") else []
            strike_count = int(row["strike_count"]) if "strike_count" in row_keys else 0
            cooldown_until_ts = float(row["cooldown_until_ts"]) if "cooldown_until_ts" in row_keys else 0.0
            consecutive_civil_turns = int(row["consecutive_civil_turns"]) if "consecutive_civil_turns" in row_keys else 0

            profile = UserPatienceProfile(
                user_id=row["user_id"],
                patience=float(row["patience"]),
                standing=Standing(row["standing"]),
                infraction_count=int(row["infraction_count"]),
                last_interaction_ts=float(row["last_interaction_ts"]),
                created_at_ts=float(row["created_at_ts"]),
                strike_count=strike_count,
                cooldown_until_ts=cooldown_until_ts,
                consecutive_civil_turns=consecutive_civil_turns,
            )

            if apply_decay:
                profile.apply_decay(current_ts=current_ts, half_life_seconds=half_life_seconds)
                conn.execute(
                    """
                    UPDATE raven_profiles
                    SET patience = ?, last_interaction_ts = ?, strike_count = ?, cooldown_until_ts = ?,
                        standing = ?, consecutive_civil_turns = ?
                    WHERE user_id = ?
                    """,
                    (profile.patience, profile.last_interaction_ts, profile.strike_count, profile.cooldown_until_ts, profile.standing.value, profile.consecutive_civil_turns, profile.user_id)
                )

        return profile

    @with_sqlite_retry()
    def save_profile(self, profile: UserPatienceProfile) -> None:
        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO raven_profiles (
                    user_id, patience, standing, infraction_count,
                    last_interaction_ts, created_at_ts, strike_count, cooldown_until_ts,
                    consecutive_civil_turns
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    patience = excluded.patience,
                    standing = excluded.standing,
                    infraction_count = excluded.infraction_count,
                    last_interaction_ts = excluded.last_interaction_ts,
                    strike_count = excluded.strike_count,
                    cooldown_until_ts = excluded.cooldown_until_ts,
                    consecutive_civil_turns = excluded.consecutive_civil_turns
                """,
                (
                    profile.user_id,
                    profile.patience,
                    profile.standing.value,
                    profile.infraction_count,
                    profile.last_interaction_ts,
                    profile.created_at_ts,
                    profile.strike_count,
                    profile.cooldown_until_ts,
                    profile.consecutive_civil_turns,
                )
            )

    @with_sqlite_retry()
    def record_interaction(
        self,
        user_id: str,
        prompt: str,
        stimulus: float,
        resulting_patience: float,
        posture: str,
        timestamp: Optional[float] = None,
    ) -> None:
        if timestamp is None:
            timestamp = time.time()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO raven_interactions (
                    user_id, prompt, stimulus, resulting_patience, posture, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (user_id, prompt, stimulus, resulting_patience, posture, timestamp)
            )
            # Prune interaction history beyond max_history_per_user to prevent unbounded database growth
            conn.execute(
                """
                DELETE FROM raven_interactions
                WHERE user_id = ? AND id NOT IN (
                    SELECT id FROM raven_interactions
                    WHERE user_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                """,
                (user_id, user_id, self.max_history_per_user)
            )

    @with_sqlite_retry()
    def get_history(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT user_id, prompt, stimulus, resulting_patience, posture, timestamp
                FROM raven_interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (user_id, limit)
            )
            rows = cursor.fetchall()
            return [dict(r) for r in reversed(rows)]

    @with_sqlite_retry()
    def reset_profile(self, user_id: str) -> None:
        now = time.time()
        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                UPDATE raven_profiles
                SET patience = 100.0,
                    standing = 'GOOD',
                    infraction_count = 0,
                    last_interaction_ts = ?
                WHERE user_id = ?
                """,
                (now, user_id)
            )
            conn.execute("DELETE FROM raven_interactions WHERE user_id = ?", (user_id,))
