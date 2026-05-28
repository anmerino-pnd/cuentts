from typing import Optional, List
from dataclasses import dataclass, asdict
from qwen_tts.inference.qwen3_tts_model import AudioLike

from cuentts.config.constants import SessionState

@dataclass
class Session:
    chat_id: int
    state: SessionState = SessionState.IDLE

    audio_path: AudioLike = ""
    ref_text: str | List[str | None] = ""
    instruction: str = ""

    def to_dict(self):
        data = asdict(self)
        data["state"] = self.state.value
        return data