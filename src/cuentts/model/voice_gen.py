import os
import io
import torch
import soundfile as sf
from typing import List, Literal
from qwen_tts import Qwen3TTSModel
from qwen_tts.inference.qwen3_tts_model import AudioLike

speakers = Literal["Vivian", "Serena", "Uncle_Fu", "Dylan", 
                   "Eric", "Ryan", "Aiden", "Ono_Anna", "Sohee"]

class TTS:
    def __init__(self, model_name: str = "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", **kwargs):
        self.model = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tts = Qwen3TTSModel.from_pretrained(
            self.model,
            device_map= "auto",
                dtype = torch.bfloat16 if self.device == "cuda" else torch.float32,
            **kwargs
        )

    def _free_space(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def generate(self, 
                 text_input: str, 
                 speaker_name: speakers,
                 instruction: str):
        
        wavs, sr = self.tts.generate_custom_voice(
            text=text_input,
            language="Spanish", # Detecta el idioma automáticamente
            speaker=speaker_name,
            instruct=instruction
        )
        self._free_space()
        return wavs, sr
    
    def custom_generate(self,
                        text_input: str, 
                        instruction: str):
        
        wavs, sr = self.tts.generate_voice_design(
            text=text_input,
            language="Spanish",
            instruct=instruction
        )
        self._free_space()
        return wavs, sr
    
    def clone_generate(self,
                       ref_audio: AudioLike, 
                       ref_text: str | List[str | None], 
                       text_input: str, 
                       instruction: str):
        voice_clone_prompt = self.tts.create_voice_clone_prompt(
            ref_audio = ref_audio,
            ref_text = ref_text,
        )

        wavs, sr = self.tts.generate_voice_clone(
            text=text_input,
            language="Spanish",
            voice_clone_prompt=voice_clone_prompt,
            instruct=instruction
        )

        self._free_space()
        return wavs, sr