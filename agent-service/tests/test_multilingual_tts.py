from pathlib import Path
import sys
import os


PROJECT_ROOT = Path(__file__).resolve().parents[1]

APP_DIR = PROJECT_ROOT / "app"

sys.path.insert(0, str(APP_DIR))


from services.multilingual_tts_service import MultilingualTTSService


tts = MultilingualTTSService()


tests = [
    {
        "language": "en",
        "name": "english_unified_test.wav",
        "text": (
            "Hello everyone. "
            "Welcome to RetailMate. "
            "How can I help you today?"
        ),
    },
    {
        "language": "hi",
        "name": "hindi_unified_test.wav",
        "text": (
            "नमस्कार दोस्तों। "
            "RetailMate में आपका स्वागत है। "
            "मैं आपकी कैसे मदद कर सकता हूँ?"
        ),
    },
    {
        "language": "kn",
        "name": "kannada_unified_test.wav",
        "text": (
            "ನಮಸ್ಕಾರ ಸ್ನೇಹಿತರೇ. "
            "RetailMate ಗೆ ಸ್ವಾಗತ. "
            "ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?"
        ),
    },
]


for test in tests:

    print()
    print("=" * 60)
    print(f"Testing language: {test['language']}")
    print("=" * 60)

    output_path = PROJECT_ROOT / test["name"]

    result = tts.text_to_speech(
        text=test["text"],
        language=test["language"],
        output_path=str(output_path),
        speed=0.95,
    )

    print("Result:")
    print(result)

    if os.name == "nt":
        os.startfile(result["audio_path"])