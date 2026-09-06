from pathlib import Path
import sys
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]

APP_DIR = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIR))


from services.sarvam_tts_service import SarvamTTSService


tts = SarvamTTSService()


text = (
    "ನಮಸ್ಕಾರ ಸ್ನೇಹಿತರೇ. "
    "RetailMate ಗೆ ಸ್ವಾಗತ. "
    "ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
)


output_path = PROJECT_ROOT / "kannada_test.wav"


result = tts.text_to_speech(
    text=text,
    output_path=str(output_path),
    speaker="shubh",
    pace=0.95,
)


print()
print("Result:")
print(result)


if os.name == "nt":
    os.startfile(result["audio_path"])