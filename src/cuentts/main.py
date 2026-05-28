import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from cuentts.telegram.webhook import router as telegram_router
from cuentts.telegram.sender import BASE_URL, BOT_TOKEN
from cuentts.config.logger import console, log_event

app = FastAPI(
    title="CuenTTs",
    description="Generador de audios",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    color = "green" if response.status_code < 400 else "red"
    log_event(
        "http",
        color=color,
        method=request.method,
        path=request.url.path,
        status=response.status_code,
    )
    return response


@app.get("/")
def root():
    return {"status": "ok", "service": "cuentts"}


@app.on_event("startup")
def verify_bot_token():
    if not BOT_TOKEN:
        console.log(
            "[red]TELEGRAM_BOT_TOKEN no está definido. Revisa tu .env "
            "(la variable debe llamarse exactamente TELEGRAM_BOT_TOKEN).[/red]"
        )
        return
    try:
        response = requests.get(f"{BASE_URL}/getMe", timeout=10)
    except requests.RequestException as exc:
        console.log(f"[red]No pude contactar a api.telegram.org:[/red] {exc}")
        return

    if response.status_code != 200 or not response.json().get("ok"):
        console.log(
            f"[red]BOT_TOKEN inválido — Telegram respondió {response.status_code}.[/red] "
            f"body={response.text}"
        )
        return

    bot = response.json()["result"]
    console.log(
        f"[green]cuentts started — bot @{bot.get('username')} ({bot.get('first_name')}) listo[/green]"
    )


app.include_router(telegram_router)
