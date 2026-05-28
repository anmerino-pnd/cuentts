import gc
import torch
from typing import List, Literal
from qwen_tts import Qwen3TTSModel
from qwen_tts.inference.qwen3_tts_model import AudioLike

from cuentts.config.logger import console


speakers = Literal["Vivian", "Serena", "Uncle_Fu", "Dylan",
                   "Eric", "Ryan", "Aiden", "Ono_Anna", "Sohee"]


class TTS:
    """Wrapper sobre Qwen3-TTS con carga perezosa por variante.

    Cada comando del bot usa una variante distinta del modelo:
      - generate  → CustomVoice
      - design    → VoiceDesign
      - clone     → Base

    Por defecto solo se mantiene **una** variante en VRAM a la vez.
    Cuando se pide otra, la anterior se descarga para liberar memoria.
    """

    BASE_NAME = "Qwen/Qwen3-TTS-12Hz-1.7B-"
    VARIANTS: dict[str, str] = {
        "custom": "CustomVoice",
        "design": "VoiceDesign",
        "clone":  "Base",
    }

    def __init__(self, single_in_memory: bool = True, **load_kwargs):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        self.single_in_memory = single_in_memory
        self.load_kwargs = load_kwargs

        self._models: dict[str, Qwen3TTSModel] = {}

    # ---------- gestión de memoria ----------

    def _free_space(self):
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def _evict_all(self):
        if not self._models:
            return
        names = list(self._models.keys())
        for name in names:
            del self._models[name]
        console.log(f"[magenta]TTS evict[/magenta] released={names}")
        self._free_space()

    def _evict_except(self, keep: str):
        to_drop = [k for k in self._models if k != keep]
        if not to_drop:
            return
        for k in to_drop:
            del self._models[k]
        console.log(f"[magenta]TTS evict[/magenta] released={to_drop} kept={keep!r}")
        self._free_space()

    # ---------- carga perezosa ----------

    def _get(self, variant: str) -> Qwen3TTSModel:
        if variant not in self.VARIANTS:
            raise ValueError(f"Variante TTS desconocida: {variant!r}")

        if self.single_in_memory and variant not in self._models:
            self._evict_except(keep=variant)

        if variant in self._models:
            return self._models[variant]

        model_name = self.BASE_NAME + self.VARIANTS[variant]
        console.log(f"[yellow]TTS load[/yellow] variant={variant!r} model={model_name!r}")
        model = Qwen3TTSModel.from_pretrained(
            model_name,
            device_map="auto",
            dtype=self.dtype,
            **self.load_kwargs,
        )
        self._models[variant] = model
        console.log(f"[green]TTS ready[/green] variant={variant!r}")
        return model

    def preload(self, *variants: str):
        """Útil si sabes que tienes VRAM de sobra y quieres precargar."""
        for v in variants:
            self._get(v)

    # ---------- helpers ----------

    @staticmethod
    def _first_wav(wavs):
        try:
            return wavs[0]
        except (TypeError, IndexError):
            return wavs

    # ---------- API pública ----------

    def generate(self,
                 text_input: str,
                 speaker_name: speakers,
                 instruction: str):
        model = self._get("custom")
        wavs, sr = model.generate_custom_voice(
            text=text_input,
            language="Spanish",
            speaker=speaker_name,
            instruct=instruction,
        )
        self._free_space()
        return self._first_wav(wavs), sr

    def custom_generate(self,
                        text_input: str,
                        instruction: str):
        model = self._get("design")
        wavs, sr = model.generate_voice_design(
            text=text_input,
            language="Spanish",
            instruct=instruction,
        )
        self._free_space()
        return self._first_wav(wavs), sr

    def clone_generate(self,
                       ref_audio: AudioLike,
                       ref_text: str | List[str | None],
                       text_input: str,
                       instruction: str):
        model = self._get("clone")
        voice_clone_prompt = model.create_voice_clone_prompt(
            ref_audio=ref_audio,
            ref_text=ref_text,
        )
        wavs, sr = model.generate_voice_clone(
            text=text_input,
            language="Spanish",
            voice_clone_prompt=voice_clone_prompt,
            instruct=instruction,
        )
        self._free_space()
        return self._first_wav(wavs), sr
