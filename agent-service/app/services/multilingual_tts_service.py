from pathlib import Path

from services.voice_service import VoiceService
from services.sarvam_tts_service import SarvamTTSService


class MultilingualTTSService:

    def __init__(self):
        print("Initializing multilingual TTS service...")

        self.kokoro = VoiceService()
        self.sarvam = SarvamTTSService()

        print("Multilingual TTS service ready.")

    def text_to_speech(
        self,
        text: str,
        language: str,
        output_path: str,
        speed: float = 0.95,
    ):
        """
        Generate speech using the appropriate TTS engine.

        Supported languages:
            en -> Kokoro
            hi -> Kokoro
            kn -> Sarvam
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        language = language.lower().strip()

        # English
        if language == "en":

            return self.kokoro.text_to_speech(
                text=text,
                output_path=output_path,
                voice="af_heart",
                speed=speed,
                lang="en-us",
            )

        # Hindi
        elif language == "hi":

            return self.kokoro.text_to_speech(
                text=text,
                output_path=output_path,
                voice="hf_alpha",
                speed=speed,
                lang="hi",
            )

        # Kannada
        elif language == "kn":

            return self.sarvam.text_to_speech(
                text=text,
                output_path=output_path,
                speaker="shubh",
                pace=speed,
            )

        else:

            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages are: en, hi, kn."
            )