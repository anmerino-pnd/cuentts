from fastapi import APIRouter, Request, BackgroundTasks

from cuentts.telegram.parser import TelegramParser
from cuentts.telegram.handlers.commands import CommandHandler
from cuentts.telegram.handlers.text import TextHandler
from cuentts.telegram.handlers.voice import VoiceHandler


router = APIRouter()

parser = TelegramParser()
command_handler = CommandHandler()
text_handler = TextHandler()
voice_handler = VoiceHandler()


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    payload = await request.json()

    parsed = parser.parse(payload)

    if not parsed:
        return {"status": "ignored"}

    if parsed.text:
        if parsed.text.startswith("/"):
            background_tasks.add_task(
                command_handler.handle,
                parsed.chat_id,
                parsed.text,
            )
        else:
            background_tasks.add_task(
                text_handler.handle,
                parsed.chat_id,
                parsed.text,
            )

    elif parsed.voice_file_id:
        background_tasks.add_task(
            voice_handler.handle,
            parsed.chat_id,
            parsed.voice_file_id,
        )

    return {"status": "ok"}