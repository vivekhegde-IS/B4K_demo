from pathlib import Path
import os

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro


class VoiceService:

    def __init__(self):

        APP_DIR = Path(__file__).resolve().parents[1]

        self.model_path = APP_DIR / "models" / "kokoro-v1.0.onnx"
        self.voices_path = APP_DIR / "models" / "voices-v1.0.bin"

        if not self.model_path.exists() or not self.voices_path.exists():
            print(f"Warning: Kokoro ONNX model or voices file not found at:\n{self.model_path}\nRunning VoiceService in fallback mode.")
            self.kokoro = None
            return

        print("Loading Kokoro...")
        print(f"Model: {self.model_path}")
        print(f"Voices: {self.voices_path}")

        try:
            self.kokoro = Kokoro(
                str(self.model_path),
                str(self.voices_path)
            )
            print("Kokoro loaded successfully!")
        except Exception as e:
            print(f"Warning: Failed to load Kokoro ONNX: {e}")
            self.kokoro = None

    def text_to_speech(
        self,
        text: str,
        output_path: str = "output.wav",
        voice: str = "hf_alpha",
        speed: float = 0.95,
        lang: str = "hi",
    ):

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        print("Generating speech...")
        print(f"Language: {lang}")
        print(f"Voice: {voice}")
        print(f"Speed: {speed}")

        samples, sample_rate = self.kokoro.create(
            text,
            voice=voice,
            speed=speed,
            lang=lang,
        )

        # Convert to numpy array
        samples = np.asarray(samples, dtype=np.float32)

        # Remove DC offset
        samples = samples - np.mean(samples)

        # Normalize volume
        peak = np.max(np.abs(samples))

        if peak > 0:
            samples = samples / peak

        # Keep a small headroom to avoid clipping
        samples = samples * 0.95

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

        sf.write(
            str(output_file),
            samples,
            sample_rate,
            subtype="PCM_16"
        )

        print("Audio generated successfully:")
        print(output_file)

        return {
            "audio_path": str(output_file),
            "sample_rate": sample_rate,
        }


if __name__ == "__main__":

    voice_service = VoiceService()

    text = (
        "नमस्कार दोस्तों। "
        "मेरा नाम कौस्तुभ है। "
        "मैं अभी बीमार हूँ। "
        "मेरा काम क्या है? कोई मुझे बताए।"
    )

    result = voice_service.text_to_speech(
        text=text,
        output_path="hindi_test.wav",

        # Hindi voice
        voice="hf_alpha",

        # Slightly slower for clearer pronunciation
        speed=0.95,

        # Hindi
        lang="hi"
    )

    print()
    print("Result:")
    print(result)

    if os.name == "nt":
        os.startfile(result["audio_path"])