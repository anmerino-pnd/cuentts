from dataclasses import dataclass

@dataclass
class UserSession:
    state: str = "idle"
    audio_path: str | None = None
    ref_text: str | None = None