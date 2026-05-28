from fastapi import APIRouter, Request, BackgroundTasks

from cuentts.telegram.parser import TelegramParser
from cuentts.telegram.handlers.commands import CommandHandler
from cuentts.telegram.handlers.text import TextHandler
from cuentts.telegram.handlers.voice import VoiceHandler
from cuentts.config.logger import console, log_event, log_exception


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
    try:
        payload = await request.json()
    except Exception:
        console.log("[red]webhook[/red] payload no es JSON válido")
        log_exception()
        return {"status": "bad-request"}

    try:
        parsed = parser.parse(payload)
    except Exception:
        log_exception()
        return {"status": "parse-error"}

    if not parsed:
        log_event("webhook.ignored", color="yellow", payload_keys=list(payload.keys()))
        return {"status": "ignored"}

    if parsed.text:
        kind = "command" if parsed.text.startswith("/") else "text"
        log_event(
            "webhook",
            chat_id=parsed.chat_id,
            kind=kind,
            text=parsed.text[:80],
        )
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
        log_event(
            "webhook",
            chat_id=parsed.chat_id,
            kind="voice",
            file_id=parsed.voice_file_id,
        )
        background_tasks.add_task(
            voice_handler.handle,
            parsed.chat_id,
            parsed.voice_file_id,
        )

    return {"status": "ok"}
