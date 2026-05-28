import json
from pathlib import Path
from threading import Lock

from cuentts.sessions.models import Session
from cuentts.config.constants import SessionState

class SessionManager:
    def __init__(self, file_path: str = "sessions.json") -> None:
        self.file_path = Path(file_path)
        self.lock = Lock()

        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")

    def _load(self) -> dict:
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def _save(self, data: dict):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get(self, chat_id: int) -> Session:
        with self.lock:
            data = self._load()
            session_data = data.get(str(chat_id))

            if not session_data:
                return Session(chat_id=chat_id)
            
            session_data["state"] = SessionState(session_data["state"])

            return Session(**session_data)
        
    def save(self, session: Session):
        with self.lock:
            data = self._load()
            data[str(session.chat_id)] = session.to_dict()
            self._save(data)

    def delete(self, chat_id: int):
        with self.lock:
            data = self._load()

            data.pop(str(chat_id), None)
            self._save(data)