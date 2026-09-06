from pathlib import Path
import base64
import os

from sarvamai import SarvamAI


class SarvamTTSService:

    def __init__(self):

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