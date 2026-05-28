import os

from dotenv import load_dotenv

ENV_KEYS: dict[str, str] = {
    "telegram_bot_token": "TELEGRAM_BOT_TOKEN"
}

def get_from_env(service: str) -> str | None:
    """Return the environment value mapped to *service*, or ``None``."""
    env_var: str | None = ENV_KEYS.get(service)
    if env_var is None:
        return None
    return os.getenv(env_var)