import json
import os
from typing import Optional, Dict, Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover
    psycopg = None
    dict_row = None


class UserStore:

    def __init__(self, json_path: str):
        self.json_path = json_path
        self.database_url = (
            os.environ.get("DATABASE_URL")
            or os.environ.get("VERCEL_POSTGRES_URL")
            or os.environ.get("POSTGRES_URL")
            or os.environ.get("PG_CONNECTION_STRING")
        )
        self.use_db = bool(self.database_url)

        if self.use_db:
            if psycopg is None:
                raise RuntimeError(
                    "psycopg[binary] is required for PostgreSQL support. "
                    "Add it to requirements.txt."
                )
            self.conn = psycopg.connect(self.database_url, autocommit=True)
            self._init_db()
        else:
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            if not os.path.exists(self.json_path):
                with open(self.json_path, "w", encoding="utf-8") as f:
                    json.dump({"users": []}, f)

    def _init_db(self) -> None:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL UNIQUE,
                    first_name TEXT,
                    last_name TEXT,
                    age INTEGER,
                    occupation TEXT,
                    password_hash TEXT NOT NULL
                )
                """
            )

    def _read(self) -> Dict[str, Any]:
        if self.use_db:
            raise RuntimeError(
                "Database-backed store does not use JSON storage.")
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        if self.use_db:
            raise RuntimeError(
                "Database-backed store does not use JSON storage.")
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _db_fetch_one(self, query: str, params: tuple) -> Optional[dict]:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def _db_execute(self, query: str, params: tuple) -> None:
        with self.conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, params)

    def exists_by_email(self, email: str) -> bool:
        return self.get_user_by_email(email) is not None

    def exists_by_username(self, username: str) -> bool:
        return self.get_user_by_username(username) is not None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        if self.use_db:
            return self._db_fetch_one(
                "SELECT * FROM users WHERE lower(email) = lower(%s) LIMIT 1",
                (email.strip(),),
            )

        data = self._read()
        for u in data.get("users", []):
            if (u.get("email") or "").strip().lower() == (email or "").strip().lower():
                return u
        return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
        if self.use_db:
            return self._db_fetch_one(
                "SELECT * FROM users WHERE lower(username) = lower(%s) LIMIT 1",
                (username.strip(),),
            )

        data = self._read()
        for u in data.get("users", []):
            if (u.get("username") or "").strip().lower() == (username or "").strip().lower():
                return u
        return None

    def create_user(
        self,
        *,
        email: str,
        username: str,
        password_hash: str,
        first_name: str = "",
        last_name: str = "",
        age: Optional[int] = None,
        occupation: str = "",
    ) -> None:
        if self.use_db:
            self._db_execute(
                "INSERT INTO users (email, username, first_name, last_name, age, occupation, password_hash) "
                "VALUES (lower(%s), lower(%s), %s, %s, %s, %s, %s)",
                (
                    email.strip(),
                    username.strip(),
                    first_name,
                    last_name,
                    age,
                    occupation,
                    password_hash,
                ),
            )
            return

        data = self._read()
        data.setdefault("users", []).append(
            {
                "email": (email or "").strip().lower(),
                "username": (username or "").strip().lower(),
                "first_name": first_name,
                "last_name": last_name,
                "age": age,
                "occupation": occupation,
                "password_hash": password_hash,
            }
        )
        self._write(data)
