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


HELP_TEXT = (
    "Comandos disponibles:\n\n"
    "• /generate [speaker] [texto] | [instrucción opcional]\n"
    "   Ejemplo: /generate Vivian Hola mundo | Habla rápido\n"
    "   Speakers: Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee\n\n"
    "• /design [prompt de voz] | [texto]\n"
    "   Ejemplo: /design Voz de locutor de radio | Bienvenidos al programa\n\n"
    "• /clone — flujo guiado paso a paso para clonar una voz.\n"
    "   1) Mandas /clone\n"
    "   2) Mandas el audio de referencia\n"
    "   3) Mandas la transcripción exacta del audio\n"
    "   4) Mandas el texto a generar (puedes añadir | instrucción opcional)\n\n"
    "• /cancel — cancela cualquier sesión en curso.\n"
    "• /help — muestra esta ayuda."
)


class CommandHandler:
    def handle(self, chat_id: int, text: str):
        session = session_manager.get(chat_id)

        parts = text.strip().split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        log_event("command", chat_id=chat_id, command=command, has_args=bool(args))

        match command:
            case "/start" | "/help":
                sender.send_message(chat_id, HELP_TEXT)

            case "/clone":
                session.state = SessionState.WAITING_CLONE_AUDIO
                session_manager.save(session)
                log_event(
                    "session.state",
                    color="magenta",
                    chat_id=chat_id,
                    state=session.state.value,
                )
                sender.send_message(chat_id, "Mándame el audio de referencia.")

            case "/design":
                if not args:
                    sender.send_message(
                        chat_id,
                        "Faltan parámetros. Uso: /design [prompt] | [texto]\n"
                        "Ejemplo: /design Voz aguda de niño | Hola mundo!",
                    )
                    return

                if "|" not in args:
                    sender.send_message(
                        chat_id,
                        "Recuerda separar el prompt y el texto con '|'.\n"
                        "Ejemplo: /design Voz de niño | Hola",
                    )
                    return

                prompt, design_text = [p.strip() for p in args.split("|", 1)]
                if not prompt or not design_text:
                    sender.send_message(
                        chat_id,
                        "Tanto el prompt como el texto son obligatorios.\n"
                        "Ejemplo: /design Voz de niño | Hola",
                    )
                    return

                sender.send_message(chat_id, "Generando audio...")
                log_event("tts.design.start", color="yellow", prompt=prompt[:60], text=design_text[:60])

                try:
                    wavs, sr = tts_service.custom_generate(
                        text_input=design_text,
                        instruction=prompt,
                    )
                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    log_event("tts.design.done", color="yellow", path=str(output_path), sr=sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as exc:
                    log_exception()
                    sender.send_message(chat_id, f"Error al generar: {exc}")

            case "/generate":
                if not args:
                    sender.send_message(
                        chat_id,
                        "Faltan parámetros. Uso: /generate [speaker] [texto] | [instrucción opcional]\n"
                        "Speakers: Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee\n"
                        "Ejemplo: /generate Vivian Hola mundo! | Habla rápido",
                    )
                    return

                gen_parts = args.split(" ", 1)
                speaker_name = gen_parts[0]
                rest_of_args = gen_parts[1] if len(gen_parts) > 1 else ""

                if not rest_of_args:
                    sender.send_message(
                        chat_id,
                        "Falta el texto a generar.\n"
                        "Uso: /generate [speaker] [texto] | [instrucción opcional]",
                    )
                    return

                instruction = ""
                if "|" in rest_of_args:
                    gen_text, instruction = [p.strip() for p in rest_of_args.split("|", 1)]
                else:
                    gen_text = rest_of_args.strip()

                sender.send_message(chat_id, f"Generando audio con la voz de {speaker_name}...")
                log_event(
                    "tts.generate.start",
                    color="yellow",
                    speaker=speaker_name,
                    text=gen_text[:60],
                    instruction=instruction[:60],
                )

                try:
                    wavs, sr = tts_service.generate(
                        text_input=gen_text,
                        speaker_name=speaker_name,
                        instruction=instruction,
                    )
                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    log_event("tts.generate.done", color="yellow", path=str(output_path), sr=sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as exc:
                    log_exception()
                    sender.send_message(chat_id, f"Error al generar: {exc}")

            case "/cancel":
                session_manager.delete(chat_id)
                log_event("session.cancel", color="magenta", chat_id=chat_id)
                sender.send_message(chat_id, "Sesión cancelada.")

            case _:
                sender.send_message(
                    chat_id,
                    f"Comando no reconocido: {command}. Usa /help para ver los comandos disponibles.",
                )
