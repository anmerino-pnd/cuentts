from uuid import uuid4

from cuentts.sessions.manager import SessionManager
from cuentts.telegram.sender import TelegramSender
from cuentts.config.constants import SessionState
from cuentts.config.paths import TEMP_AUDIO_DIR
from cuentts.config.logger import log_event, log_exception


session_manager = SessionManager()
sender = TelegramSender()


class VoiceHandler:
    def handle(self, chat_id: int, voice_file_id: str):
        session = session_manager.get(chat_id)
        log_event(
            "voice.received",
            chat_id=chat_id,
            state=session.state.value,
            file_id=voice_file_id,
        )

        match session.state:
            case SessionState.WAITING_CLONE_AUDIO:
                try:
                    file_path = sender.get_file(voice_file_id)
                    if not file_path:
                        sender.send_message(chat_id, "Error al obtener el audio de Telegram.")
                        return

                    audio_data = sender.download_file(file_path)
                    local_audio_path = TEMP_AUDIO_DIR / f"{uuid4()}.ogg"
                    with open(local_audio_path, "wb") as f:
                        f.write(audio_data)

                    session.audio_path = str(local_audio_path)
                    session.state = SessionState.WAITING_CLONE_TEXT
                    session_manager.save(session)

                    log_event(
                        "session.state",
                        color="magenta",
                        chat_id=chat_id,
                        state=session.state.value,
                        audio_path=str(local_audio_path),
                    )
                    sender.send_message(chat_id, "Ahora manda el texto EXACTO del audio.")
                except Exception as exc:
                    log_exception()
                    sender.send_message(chat_id, f"Error procesando el audio: {exc}")

            case _:
                sender.send_message(
                    chat_id,
                    "Recibí un audio pero no hay una sesión activa esperándolo. "
                    "Usa /clone si quieres iniciar el flujo de clonación.",
                )
