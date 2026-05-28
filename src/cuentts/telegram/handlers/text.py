import soundfile as sf
from uuid import uuid4

from cuentts.sessions.manager import SessionManager
from cuentts.telegram.sender import TelegramSender
from cuentts.config.constants import SessionState
from cuentts.telegram.tts_instance import tts_service
from cuentts.config.paths import TEMP_AUDIO_DIR
from cuentts.config.logger import log_event, log_exception


session_manager = SessionManager()
sender = TelegramSender()


class TextHandler:
    def handle(self, chat_id: int, text: str):
        session = session_manager.get(chat_id)
        log_event(
            "text.received",
            chat_id=chat_id,
            state=session.state.value,
            text=text[:80],
        )

        match session.state:
            case SessionState.WAITING_CLONE_TEXT:
                session.ref_text = text
                session.state = SessionState.WAITING_CLONE_GENERATION_TEXT
                session_manager.save(session)

                log_event(
                    "session.state",
                    color="magenta",
                    chat_id=chat_id,
                    state=session.state.value,
                )
                sender.send_message(
                    chat_id,
                    "Ahora manda el texto que quieres generar "
                    "(puedes añadir una instrucción opcional separada por '|').",
                )

            case SessionState.WAITING_CLONE_GENERATION_TEXT:
                sender.send_message(chat_id, "Clonando voz y generando audio...")

                instruction = ""
                if "|" in text:
                    gen_text, instruction = [p.strip() for p in text.split("|", 1)]
                else:
                    gen_text = text.strip()

                log_event(
                    "tts.clone.start",
                    color="yellow",
                    ref_audio=session.audio_path,
                    text=gen_text[:60],
                    instruction=instruction[:60],
                )

                try:
                    wavs, sr = tts_service.clone_generate(
                        ref_audio=session.audio_path,
                        ref_text=session.ref_text,
                        text_input=gen_text,
                        instruction=instruction,
                    )

                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    log_event("tts.clone.done", color="yellow", path=str(output_path), sr=sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as exc:
                    log_exception()
                    sender.send_message(chat_id, f"Error al generar: {exc}")
                finally:
                    session_manager.delete(chat_id)
                    log_event("session.cleared", color="magenta", chat_id=chat_id)

            case _:
                sender.send_message(
                    chat_id,
                    "No tengo ninguna acción esperando texto. Usa /help para ver los comandos.",
                )
