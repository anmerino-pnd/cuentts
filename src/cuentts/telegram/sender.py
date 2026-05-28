import os
import requests

from cuentts.config.credentials import get_from_env
from cuentts.config.logger import console, log_event


BOT_TOKEN = get_from_env("telegram_bot_token")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def _log_response(method: str, response: requests.Response) -> None:
    if 200 <= response.status_code < 300:
        log_event(f"telegram.{method}", color="green", status=response.status_code)
    else:
        console.log(
            f"[red]telegram.{method} {response.status_code}[/red] body={response.text}"
        )


class TelegramSender:
    def send_message(self, chat_id: int, text: str):
        response = requests.post(
            f"{BASE_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
        )
        _log_response("sendMessage", response)

    def send_voice(self, chat_id: int, file_path: str):
        size = os.path.getsize(file_path) if os.path.exists(file_path) else -1
        log_event("telegram.sendVoice.start", path=file_path, size=size)
        with open(file_path, "rb") as audio:
            response = requests.post(
                f"{BASE_URL}/sendVoice",
                data={"chat_id": chat_id},
                files={"voice": audio},
            )
        _log_response("sendVoice", response)

    def get_file(self, file_id: str) -> str | None:
        response = requests.get(
            f"{BASE_URL}/getFile",
            params={"file_id": file_id},
        )
        _log_response("getFile", response)
        if response.status_code == 200:
            return response.json().get("result", {}).get("file_path")
        return None

    def download_file(self, file_path: str) -> bytes:
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        response = requests.get(file_url)
        _log_response("downloadFile", response)
        response.raise_for_status()
        return response.content
