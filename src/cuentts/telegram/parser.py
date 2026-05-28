from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedTelegramMessage:
    chat_id: int

    text: Optional[str] = None
    voice_file_id: Optional[str] = None


class TelegramParser:
    def parse(self, payload: dict) -> ParsedTelegramMessage | None:
        message = payload.get("message")

        if not message:
            return None

        chat_id = message["chat"]["id"]

        if "text" in message:
            return ParsedTelegramMessage(
                chat_id=chat_id,
                text=message["text"],
            )

        if "voice" in message:
            return ParsedTelegramMessage(
                chat_id=chat_id,
                voice_file_id=message["voice"]["file_id"],
            )

        return None