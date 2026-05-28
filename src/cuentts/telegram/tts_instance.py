from cuentts.model.voice_gen import TTS
from cuentts.config.logger import console


class _LazyTTS:
    """Carga el modelo en el primer acceso real, no al importar el módulo."""

    def __init__(self):
        self._tts: TTS | None = None

    def _ensure(self) -> TTS:
        if self._tts is None:
            console.log("[yellow]Cargando modelo TTS...[/yellow]")
            self._tts = TTS()
            console.log("[green]Modelo TTS listo[/green]")
        return self._tts

    def __getattr__(self, name):
        return getattr(self._ensure(), name)


tts_service = _LazyTTS()
