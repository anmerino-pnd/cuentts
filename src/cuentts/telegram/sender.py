import rich
import requests
from cuentts.config.credentials import get_from_env


BOT_TOKEN = get_from_env("TELEGRAM_BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

class TelegramSender:
    def send_message(self, chat_id: int, text: str):
        request = requests.post(
            f"{BASE_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
        )

        rich.print(request)
        

    def send_voice(self, chat_id: int, file_path: str):
        with open(file_path, "rb") as audio:
            request = requests.post(
                f"{BASE_URL}/sendVoice",
                data={
                    "chat_id": chat_id,
                },
                files={
                    "voice": audio,
                },
            )
        rich.print(request)

    def get_file(self, file_id: str) -> str | None:
        request = requests.get(
            f"{BASE_URL}/getFile",
            params={"file_id": file_id}
        )
        if request.status_code == 200:
            return request.json().get("result", {}).get("file_path")
        return None

    def download_file(self, file_path: str) -> bytes:
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        response = requests.get(file_url)
        response.raise_for_status()
        return response.content
