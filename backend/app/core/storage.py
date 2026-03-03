import time
import re
from typing import Any

SessionState = dict[str, Any]

class InMemoryStore:
    def __init__(self) -> None:
        self.sessions: dict[str, SessionState] = {}
        self.places_cache: dict[str, list[dict[str, Any]]] = {}

    def get_session(self, session_id: str) -> SessionState:
        s = self.sessions.get(session_id)
        if not s:
            s = {
                "session_id": session_id,
                "created_at": time.time(),
                "updated_at": time.time(),
                "interests": [],
                "history": [],
                "last_interest": None,
                "last_examples": None,
            }
            self.sessions[session_id] = s
        s["updated_at"] = time.time()
        return s

    @staticmethod
    def normalize_interest(x: str) -> str:
        x = x.strip()
        x = re.sub(r"\s+", " ", x)
        return x.lower()

    def add_interest_deduped(self, session: SessionState, interest: str) -> tuple[bool, str | None]:
        raw = (interest or "").strip()
        if not raw:
            return False, None

        norm = self.normalize_interest(raw)
        existing = {self.normalize_interest(i) for i in session["interests"]}
        if norm in existing:
            return False, None

        canonical = raw[:1].upper() + raw[1:]
        session["interests"].append(canonical)
        return True, canonical