from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class ChatSettings:
    chat_id: int
    your_name: str
    partner_name: str
    anniversary_date: str | None
    daily_time: str | None


class Database:
    def __init__(self, db_path: str = "bot.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    chat_id INTEGER PRIMARY KEY,
                    your_name TEXT NOT NULL,
                    partner_name TEXT NOT NULL,
                    anniversary_date TEXT,
                    daily_time TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def upsert_chat_names(self, chat_id: int, your_name: str, partner_name: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO chats(chat_id, your_name, partner_name)
                VALUES(?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                  your_name=excluded.your_name,
                  partner_name=excluded.partner_name
                """,
                (chat_id, your_name, partner_name),
            )

    def get_chat(self, chat_id: int) -> ChatSettings | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM chats WHERE chat_id=?", (chat_id,)).fetchone()
            if not row:
                return None
            return ChatSettings(**dict(row))

    def set_anniversary(self, chat_id: int, date_value: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE chats SET anniversary_date=? WHERE chat_id=?",
                (date_value, chat_id),
            )

    def set_daily_time(self, chat_id: int, time_value: str | None) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE chats SET daily_time=? WHERE chat_id=?",
                (time_value, chat_id),
            )

    def add_note(self, chat_id: int, content: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO notes(chat_id, content) VALUES(?, ?)",
                (chat_id, content),
            )

    def list_notes(self, chat_id: int) -> list[sqlite3.Row]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, content, created_at FROM notes WHERE chat_id=? ORDER BY id DESC",
                (chat_id,),
            ).fetchall()
            return list(rows)

    def delete_note(self, chat_id: int, note_id: int) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM notes WHERE chat_id=? AND id=?",
                (chat_id, note_id),
            )
            return cursor.rowcount

    def chats_with_daily_time(self) -> list[ChatSettings]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM chats WHERE daily_time IS NOT NULL"
            ).fetchall()
            return [ChatSettings(**dict(row)) for row in rows]
