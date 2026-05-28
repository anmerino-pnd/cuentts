# Cuentts - Telegram TTS Bot

Un bot de Telegram avanzado impulsado por el modelo [Qwen3-TTS](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice) y construido con **FastAPI**. Te permite interactuar directamente desde Telegram para generar voces de texto a voz, crear voces personalizadas (voice design), o clonar tu propia voz paso a paso.

## Características 🌟
El bot expone las tres funciones principales del modelo TTS mediante comandos intuitivos:

- **Generación Básica**: Usa voces preentrenadas (Vivian, Serena, Uncle_Fu, Dylan, etc.).
- **Diseño de Voz**: Describe el tipo de voz que quieres (ej: "voz aguda de locutor", "tono feliz") y obtén un audio personalizado.
- **Clonación de Voz**: Permite mandar un mensaje de voz, su transcripción, y un texto objetivo para que el modelo hable con la voz clonada del audio.

## Requisitos 🛠️
- Python >= 3.13
- Token de la API de tu bot de Telegram (obtenido a través de [@BotFather](https://t.me/BotFather))
- ngrok (o cualquier otro servicio para exponer puertos locales, a menos que despliegues en la nube)

## Instalación y Ejecución 🚀

1. **Clona el repositorio:**
   ```bash
   git clone <url-de-tu-repo>
   cd cuentts
   ```

2. **Instala las dependencias:**
   Puedes instalarlo usando el archivo `pyproject.toml` (o con `uv` si lo prefieres):
   ```bash
   pip install -e .
   ```

3. **Variables de Entorno:**
   Asegúrate de crear un archivo `.env` en la raíz del proyecto y añadir el token de tu bot de Telegram:
   ```env
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```

4. **Inicia el servidor:**
   Inicia la aplicación FastAPI (asegúrate de saber en qué puerto se levanta, comúnmente el `8000`).
   ```bash
   uvicorn src.cuentts.main:app --reload
   ```

## Configuración del Webhook de Telegram 🔗 (MUY IMPORTANTE)

Para que Telegram sepa a dónde enviar los mensajes que recibe el bot, **debes configurar el webhook**. 

Si estás probando el bot de manera local, primero usa `ngrok` para exponer tu puerto:
```bash
ngrok http 8000
```

Ngrok te dará una URL (ej: `https://<YOUR_NGROK_URL>.ngrok-free.app`). Con esa URL, visita el siguiente enlace en tu navegador web para registrar el webhook con Telegram (asegúrate de reemplazar los campos de `<YOUR_API_TOKEN>` y `<YOUR_NGROK_URL>`):

```
https://api.telegram.org/bot<YOUR_API_TOKEN>/setWebhook?url=<YOUR_NGROK_URL>/webhook
```

Deberías ver una respuesta como `{"ok":true,"result":true,"description":"Webhook was set"}`.

## Uso de los Comandos 💬

### `/generate`
Genera un audio utilizando una de las voces base del modelo.
**Uso:** `/generate [speaker] [texto] | [instrucción opcional]`
**Voces válidas:** Vivian, Serena, Uncle_Fu, Dylan, Eric, Ryan, Aiden, Ono_Anna, Sohee.
**Ejemplo:**
```text
/generate Vivian Hola, soy Vivian y te hablo desde Telegram | Habla muy rápido y alegre
```

### `/design`
Diseña una voz desde cero proporcionando una descripción.
**Uso:** `/design [descripción/prompt] | [texto]`
**Ejemplo:**
```text
/design Voz de hombre mayor hablando como en la radio | Bienvenidos a la transmisión del día de hoy
```

### `/clone`
Un flujo guiado paso a paso para clonar una voz de referencia.
1. Envía el comando `/clone` en el chat.
2. El bot te pedirá que le mandes un **audio o mensaje de voz**.
3. Una vez enviado y procesado, te pedirá que mandes un texto con la **transcripción exacta** de lo que se dice en ese audio.
4. Finalmente, te pedirá que le mandes **el nuevo texto que quieres generar** (puedes anexar de manera opcional una instrucción al final separada por el símbolo `|`).
5. ¡Recibirás tu audio clonado!

---

*Desarrollado con ❤️ para cuentts*
