from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import uuid

from services.multilingual_tts_service import MultilingualTTSService


app = FastAPI(
    title="RetailMate Agent Service",
    version="1.0.0"
)


# --------------------------------------------------
# Multilingual Voice Service
# --------------------------------------------------

voice_service = MultilingualTTSService()


# --------------------------------------------------
# Request Schema
# --------------------------------------------------

class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"
    speed: float = 0.95


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": "agent-service"
    }


# --------------------------------------------------
# Text To Speech
# --------------------------------------------------

@app.post("/api/voice/tts")
def text_to_speech(request: TextToSpeechRequest):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    language = request.language.lower().strip()

    supported_languages = {
        "en",
        "hi",
        "kn"
    }

    if language not in supported_languages:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {language}. "
                f"Supported languages are: en, hi, kn."
            )
        )

    try:

        filename = f"tts_{uuid.uuid4().hex}.wav"

        output_path = (
            Path(__file__).resolve().parents[1]
            / "audio"
            / filename
        )

        result = voice_service.text_to_speech(
            text=request.text,
            language=language,
            output_path=str(output_path),
            speed=request.speed
        )

        return {
            "success": True,
            "language": language,
            "audio_path": result["audio_path"],
            "sample_rate": result["sample_rate"],
            "audio_url": f"/api/voice/audio/{filename}"
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# --------------------------------------------------
# Get Generated Audio
# --------------------------------------------------

@app.get("/api/voice/audio/{filename}")
def get_audio(filename: str):

    audio_path = (
        Path(__file__).resolve().parents[1]
        / "audio"
        / filename
    )

    if not audio_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Audio file not found."
        )

    return FileResponse(
        path=str(audio_path),
        media_type="audio/wav",
        filename=filename
    )