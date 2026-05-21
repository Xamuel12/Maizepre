import json
import os
from typing import Optional, Dict, Any


class UserStore:

    def __init__(self, json_path: str):
        self.json_path = json_path
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump({"users": []}, f)

    def _read(self) -> Dict[str, Any]:
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def exists_by_email(self, email: str) -> bool:
        return self.get_user_by_email(email) is not None

    def exists_by_username(self, username: str) -> bool:
        return self.get_user_by_username(username) is not None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        data = self._read()
        for u in data.get("users", []):
            if (u.get("email") or "").strip().lower() == (email or "").strip().lower():
                return u
        return None

    def get_user_by_username(self, username: str) -> Optional[dict]:
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
