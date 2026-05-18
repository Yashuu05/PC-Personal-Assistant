"""
SQLite3 Database Utility for Personal Assistant (LOQ).
Manages persistence for assistant configuration settings, conversation logs,
interaction latency metrics, and command execution frequency tracking.
"""

import os
import sqlite3
from datetime import datetime
from utils.logger import logging as log

class AssistantMemory:
    def __init__(self, db_path=None):
        if not db_path:
            # Resolve to root-level data/memory.db
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(project_root, "data", "memory.db")
        
        self.db_path = db_path
        # Auto-create parent directory structure if not exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        log.info(f"Initializing AssistantMemory database at: {self.db_path}")
        self.init_database()

    def init_database(self):
        """Initializes settings, history log, and command usage tracking tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 1. Settings Table: Persistent configs (Assistant Name, Voice engine, etc.)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                
                # 2. History Log Table: Stores all user audio transcripts, assistant TTS replies, commands, and latency
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT DEFAULT (datetime('now', 'localtime')),
                        user_text TEXT,
                        response TEXT,
                        command_executed TEXT,
                        latency_ms REAL
                    )
                """)
                
                # 3. Command Usage Table: Stores counter details of commands invoked
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_usage (
                        command TEXT PRIMARY KEY,
                        use_count INTEGER DEFAULT 0
                    )
                """)
                
                conn.commit()
                log.info("Database schemas verified and loaded successfully.")
        except Exception as e:
            log.error(f"Error during SQLite database initialization: {e}")
            raise e

    def get_setting(self, key, default=None):
        """Fetches the value of a specific persistent setting key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    return row[0]
                return default
        except Exception as e:
            log.error(f"Failed to fetch setting '{key}' from database: {e}")
            return default

    def set_setting(self, key, value):
        """Saves or updates a persistent setting key-value pair."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, str(value))
                )
                conn.commit()
                log.info(f"Database setting saved: '{key}' -> '{value}'")
                return True
        except Exception as e:
            log.error(f"Failed to set setting '{key}' to '{value}': {e}")
            return False

    def log_interaction(self, user_text, response, command_executed, latency_ms):
        """Logs a conversation cycle to the history table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO history (user_text, response, command_executed, latency_ms)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_text, response, command_executed, latency_ms)
                )
                conn.commit()
                log.info(f"Interaction logged: User Spoke='{user_text}', Latency={latency_ms:.2f}ms")
                return True
        except Exception as e:
            log.error(f"Failed to log interaction to database: {e}")
            return False

    def increment_command_usage(self, command):
        """Increments the frequency of an executed command."""
        if not command:
            return False
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO command_usage (command, use_count)
                    VALUES (?, 1)
                    ON CONFLICT(command) DO UPDATE SET use_count = use_count + 1
                    """,
                    (command,)
                )
                conn.commit()
                log.info(f"Command frequency incremented: '{command}'")
                return True
        except Exception as e:
            log.error(f"Failed to increment command usage counter: {e}")
            return False

    def get_history(self, limit=50):
        """
        Retrieves recent conversation logs from history.
        Returns entries sorted in chronological order (oldest to newest)
        so they read sequentially inside log console blocks.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Fetch recent items ordered descending, then reverse in Python for chronological output
                cursor.execute(
                    """
                    SELECT timestamp, user_text, response, command_executed, latency_ms
                    FROM history
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                rows = cursor.fetchall()
                # Reverse list to make it chronological (oldest first)
                rows.reverse()
                return rows
        except Exception as e:
            log.error(f"Failed to query interaction logs from history table: {e}")
            return []

    def get_most_used_commands(self, limit=5):
        """Fetches the top used commands ordered by invocation frequency."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT command, use_count
                    FROM command_usage
                    ORDER BY use_count DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                return cursor.fetchall()
        except Exception as e:
            log.error(f"Failed to query command usage metrics: {e}")
            return []

    def clear_history(self):
        """Wipes the interaction history and command usage counters."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                cursor.execute("DELETE FROM command_usage")
                conn.commit()
                log.info("Database conversation logs and command usage metrics wiped successfully.")
                return True
        except Exception as e:
            log.error(f"Failed to clear database logs: {e}")
            return False
