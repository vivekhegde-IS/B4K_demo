from pathlib import Path
import base64
import os
from collections.abc import Iterator

class SarvamTTSService:

    def __init__(self):

        try:
            from sarvamai import SarvamAI
        except ImportError as exc:
            raise RuntimeError(
                "Sarvam SDK is not installed. Install the 'sarvamai' package "
                "to enable Kannada TTS."
            ) from exc

        api_key = os.getenv("SARVAM_API_KEY")

        if not api_key:
            raise RuntimeError(
                "SARVAM_API_KEY environment variable is not set."
            )

        self.client = SarvamAI(
            api_subscription_key=api_key
        )

    def text_to_speech(
        self,
        text: str,
        output_path: str = "kannada_test.wav",
        speaker: str = "shubh",
        pace: float = 0.95,
    ):

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        if len(text) > 2500:
            raise ValueError(
                "Sarvam Bulbul v3 REST request supports "
                "a maximum of 2500 characters."
            )

        print("Generating Kannada speech...")
        print(f"Speaker: {speaker}")
        print(f"Pace: {pace}")

        response = self.client.text_to_speech.convert(
            text=text,
            model="bulbul:v3",
            language_code="kn-IN",
            speaker=speaker,
            pace=pace,
        )

        if not response.audios:
            raise RuntimeError(
                "Sarvam returned no audio."
            )

        audio_base64 = response.audios[0]

        audio_bytes = base64.b64decode(
            audio_base64
        )

        output_file = Path(output_path)

        if not output_file.is_absolute():
            output_file = (
                Path(__file__).resolve().parents[2]
                / output_file
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(output_file, "wb") as f:
            f.write(audio_bytes)

        print("Kannada audio generated:")
        print(output_file)

        return {
            "audio_path": str(output_file),
            "sample_rate": 24000,
            "language": "kn-IN",
            "speaker": speaker,
        }

    def stream_audio(
        self,
        text: str,
        language_code: str,
        speaker: str = "shubh",
        pace: float = 0.95,
    ) -> Iterator[bytes]:
        """Yield Bulbul v3 MP3 chunks as soon as Sarvam emits them."""

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        if len(text) > 2500:
            raise ValueError(
                "Sarvam Bulbul v3 streaming supports a maximum of 2500 characters."
            )

        with self.client.text_to_speech_streaming.connect(
            model="bulbul:v3",
            send_completion_event="true",
        ) as socket:
            socket.configure(
                target_language_code=language_code,
                speaker=speaker,
                pace=pace,
                speech_sample_rate=24000,
                output_audio_codec="mp3",
                min_buffer_size=50,
                max_chunk_length=150,
            )
            socket.convert(text.strip())
            socket.flush()

            while True:
                message = socket.recv()
                message_type = getattr(message, "type", None)

                if message_type == "audio":
                    audio = getattr(getattr(message, "data", None), "audio", None)
                    if audio:
                        yield base64.b64decode(audio)
                    continue

                if message_type == "error":
                    error_data = getattr(message, "data", None)
                    raise RuntimeError(
                        getattr(error_data, "message", "Sarvam streaming TTS failed.")
                    )

                if message_type == "event":
                    event_data = getattr(message, "data", None)
                    if getattr(event_data, "event_type", None) == "final":
                        break