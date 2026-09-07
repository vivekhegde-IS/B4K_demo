from pathlib import Path
from collections.abc import Iterator

from app.services.voice_service import VoiceService
from app.services.sarvam_tts_service import SarvamTTSService

class MultilingualTTSService:

    def __init__(self):
        self.kokoro = VoiceService()
        self.sarvam = None

    def _get_sarvam(self):
        if self.sarvam is None:
            self.sarvam = SarvamTTSService()
        return self.sarvam

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

            return self._get_sarvam().text_to_speech(
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

    def stream_audio(
        self,
        text: str,
        language: str,
        speed: float = 0.95,
    ) -> Iterator[bytes]:
        """Stream Bulbul v3 audio for low-latency browser playback."""

        language_code = {
            "en": "en-IN",
            "hi": "hi-IN",
            "kn": "kn-IN",
        }.get(language.lower().strip())

        if not language_code:
            raise ValueError(f"Unsupported language: {language}")

        yield from self._get_sarvam().stream_audio(
            text=text,
            language_code=language_code,
            speaker="shubh",
            pace=speed,
        )