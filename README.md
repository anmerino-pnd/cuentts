# Cuentts - Telegram TTS Bot

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.11%20cu128-EE4C2C?logo=pytorch&logoColor=white)
![Qwen](https://img.shields.io/badge/Model-Qwen3--TTS-purple?logo=huggingface&logoColor=white)
![uv](https://img.shields.io/badge/uv-Blazing_Fast-magenta?logo=python)

An advanced Telegram bot powered by the [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) model and built with **FastAPI**. It allows you to interact directly from Telegram to generate text-to-speech voices, create custom voices (voice design), or clone your own voice step by step.

**Repository:** [https://github.com/anmerino-pnd/cuentts](https://github.com/anmerino-pnd/cuentts)

## Features 🌟
The bot exposes the three main functions of the TTS model through intuitive commands:

- **Basic Generation**: Use pre-trained voices (Vivian, Serena, Uncle_Fu, Dylan, etc.).
- **Voice Design**: Describe the type of voice you want (e.g., "high-pitched radio host voice", "happy tone") and get a custom audio.
- **Voice Cloning**: Send a voice message, its transcription, and a target text to make the model speak with the cloned voice from your audio.

## Requirements 🛠️
- Python >= 3.13
- Telegram Bot API Token (obtained via [@BotFather](https://t.me/BotFather))
- ngrok (or any other service to expose local ports, unless you deploy in the cloud)
- [uv](https://github.com/astral-sh/uv) package manager (recommended for fast dependency resolution)

## Installation & Setup 🚀

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anmerino-pnd/cuentts.git
   cd cuentts
   ```

2. **Install dependencies:**
   We use `uv` for blazing-fast package management. First, install the base dependencies:
   ```bash
   uv pip install -e .
   ```

3. **Install PyTorch with CUDA support (Crucial Step):**
   To ensure the model runs efficiently on your GPU (as noted in the project notebooks), you must install the specific PyTorch version with CUDA 12.8 support. Run the following `uv` commands:
   ```bash
   uv pip uninstall torch torchvision torchaudio
   uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
   ```

4. **Environment Variables:**
   Create a `.env` file in the root of the project and add your Telegram bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_here
   ```

5. **Start the server:**
   Start the FastAPI application (it commonly runs on port `8000`).
   ```bash
   uvicorn cuentts.main:app
   ```
   On startup you should see a green `cuentts started — bot @<your_bot>` line in the console. The TTS model loads lazily on the first generation request. If you instead see a red `BOT_TOKEN inválido` or `TELEGRAM_BOT_TOKEN no está definido`, fix your `.env` before continuing — every Telegram API call will return 404 until the token is valid.

   **About `--reload`:** avoid it for normal use. `SessionManager` rewrites `sessions.json` on every state change, and `--reload` watches the whole working directory by default — each session save would trigger a reload and re-download the multi-GB TTS model. If you really want hot-reload while developing, scope it tightly:
   ```bash
   uvicorn cuentts.main:app --reload --reload-dir src/cuentts
   ```

## Telegram Webhook Configuration 🔗 (VERY IMPORTANT)

For Telegram to know where to send the messages your bot receives, **you must configure the webhook**. 

If you are testing the bot locally, first use `ngrok` to expose your port:
```bash
ngrok http 8000
```

Ngrok will give you a URL (e.g., `https://<YOUR_NGROK_URL>.ngrok-free.app`). Using that URL, visit the following link in your web browser to register the webhook with Telegram (make sure to replace the `<YOUR_API_TOKEN>` and `<YOUR_NGROK_URL>` fields):

```
https://api.telegram.org/bot<YOUR_API_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhook
```

You should see a response like `{"ok":true,"result":true,"description":"Webhook was set"}`.

### Troubleshooting 🩺

- **`POST /webhook 200 OK` followed by `<Response [404]>` in the console.** This means FastAPI received the update fine, but the call back to `api.telegram.org` returned 404 — almost always an invalid `TELEGRAM_BOT_TOKEN`. With the current logging you'll now see the actual body (e.g. `{"ok":false,"error_code":404,"description":"Not Found"}`). Double-check `.env`: the value must be the raw token from @BotFather (`123456:ABC-DEF...`), without quotes or trailing spaces.
- **Browser hits to `/webhook` give 405.** That's expected: only `POST` is registered. Use `GET /` for a quick health-check; it should return `{"status":"ok","service":"cuentts"}`.
- **Telegram doesn't reach the bot at all.** Make sure the URL passed to `setWebhook` ends exactly in `/webhook` (no trailing slash) and that ngrok is still running on the same URL you registered.

## Commands Usage 💬

### `/generate`
Generates an audio using one of the model's base voices.
**Usage:** `/generate [speaker] [text] | [optional instruction]`
**Valid voices:** Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee.
**Example:**
```text
/generate Vivian Hello, I am Vivian and I am speaking from Telegram | Speak very fast and happily
```

### `/design`
Designs a voice from scratch by providing a description.
**Usage:** `/design [description/prompt] | [text]`
**Example:**
```text
/design Voice of an older man speaking like on the radio | Welcome to today's broadcast
```

### `/clone`
A guided step-by-step flow to clone a reference voice.
1. Send the `/clone` command in the chat.
2. The bot will ask you to send an **audio or voice message**.
3. Once sent and processed, it will ask you to send a text with the **exact transcription** of what is said in that audio.
4. Finally, it will ask you to send **the new text you want to generate** (you can optionally append an instruction at the end separated by the `|` symbol).
5. You will receive your cloned audio!

---

*Developed with ❤️ for cuentts*
