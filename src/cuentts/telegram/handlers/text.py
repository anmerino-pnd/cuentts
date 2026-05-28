import soundfile as sf
from uuid import uuid4

from cuentts.sessions.manager import SessionManager
from cuentts.telegram.sender import TelegramSender
from cuentts.config.constants import SessionState
from cuentts.telegram.tts_instance import tts_service
from cuentts.config.paths import TEMP_AUDIO_DIR


session_manager = SessionManager()
sender = TelegramSender()


class TextHandler:
    def handle(self, chat_id: int, text: str):
        session = session_manager.get(chat_id)

        match session.state:
            case SessionState.WAITING_CLONE_TEXT:
                session.ref_text = text
                session.state = SessionState.WAITING_CLONE_GENERATION_TEXT

                session_manager.save(session)

                sender.send_message(
                    chat_id,
                    "Ahora manda el texto que quieres generar (puedes añadir una instrucción opcional separada por '|').",
                )

            case SessionState.WAITING_CLONE_GENERATION_TEXT:
                sender.send_message(chat_id, "Clonando voz y generando audio...")

                instruction = ""
                if "|" in text:
                    gen_text, instruction = [p.strip() for p in text.split("|", 1)]
                else:
                    gen_text = text.strip()

                try:
                    wavs, sr = tts_service.clone_generate(
                        ref_audio=session.audio_path,
                        ref_text=session.ref_text,
                        text_input=gen_text,
                        instruction=instruction
                    )

                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as e:
                    sender.send_message(chat_id, f"Error al generar: {e}")
                finally:
                    # Siempre limpiamos la sesión al terminar (o si hay error en la generación final)
                    session_manager.delete(chat_id)