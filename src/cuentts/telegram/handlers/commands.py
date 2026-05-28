import soundfile as sf
from uuid import uuid4

from cuentts.sessions.manager import SessionManager
from cuentts.telegram.sender import TelegramSender
from cuentts.config.constants import SessionState
from cuentts.telegram.tts_instance import tts_service
from cuentts.config.paths import TEMP_AUDIO_DIR


session_manager = SessionManager()
sender = TelegramSender()


class CommandHandler:
    def handle(self, chat_id: int, text: str):
        session = session_manager.get(chat_id)

        # Split command and args
        parts = text.strip().split(" ", 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        match command:
            case "/clone":
                session.state = SessionState.WAITING_CLONE_AUDIO
                session_manager.save(session)

                sender.send_message(
                    chat_id,
                    "Mándame el audio de referencia.",
                )

            case "/design":
                if not args:
                    sender.send_message(
                        chat_id,
                        "Faltan parámetros. Uso: `/design [prompt] | [texto]`\nEjemplo: `/design Voz aguda de niño | Hola mundo!`"
                    )
                    return
                
                # Parse prompt and text
                if "|" in args:
                    prompt, design_text = [p.strip() for p in args.split("|", 1)]
                else:
                    # fallback if no |
                    sender.send_message(chat_id, "Recuerda separar el prompt y el texto con '|'. Ejemplo: `/design Voz de niño | Hola`")
                    return
                
                sender.send_message(chat_id, "Generando audio...")
                
                try:
                    wavs, sr = tts_service.custom_generate(
                        text_input=design_text,
                        instruction=prompt
                    )
                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as e:
                    sender.send_message(chat_id, f"Error al generar: {e}")

            case "/generate":
                if not args:
                    sender.send_message(
                        chat_id,
                        "Faltan parámetros. Uso: `/generate [speaker] [texto] | [instrucción opcional]`\nSpeakers válidos: Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee\nEjemplo: `/generate Vivian Hola mundo! | Habla rápido`"
                    )
                    return
                
                # Extract speaker
                gen_parts = args.split(" ", 1)
                speaker_name = gen_parts[0]
                rest_of_args = gen_parts[1] if len(gen_parts) > 1 else ""
                
                if not rest_of_args:
                    sender.send_message(chat_id, "Falta el texto a generar. Uso: `/generate [speaker] [texto]`")
                    return
                
                instruction = ""
                if "|" in rest_of_args:
                    gen_text, instruction = [p.strip() for p in rest_of_args.split("|", 1)]
                else:
                    gen_text = rest_of_args.strip()
                    
                sender.send_message(chat_id, f"Generando audio con la voz de {speaker_name}...")
                
                try:
                    wavs, sr = tts_service.generate(
                        text_input=gen_text,
                        speaker_name=speaker_name,
                        instruction=instruction
                    )
                    output_path = TEMP_AUDIO_DIR / f"{uuid4()}.wav"
                    sf.write(str(output_path), wavs, sr)
                    sender.send_voice(chat_id, str(output_path))
                except Exception as e:
                    sender.send_message(chat_id, f"Error al generar: {e}")

            case "/cancel":
                session_manager.delete(chat_id)
                sender.send_message(
                    chat_id,
                    "Sesión cancelada.",
                )