from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cuentts.telegram.webhook import router as telegram_router

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

app.include_router(telegram_router)