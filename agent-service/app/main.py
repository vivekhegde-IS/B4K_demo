from dotenv import load_dotenv

load_dotenv()

from pathlib import Path
from typing import Optional
import uuid
import logging
import time
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

from app.agent.workflow import AgentWorkflow
from app.services.multilingual_tts_service import MultilingualTTSService
from app.services.language import normalize_language, speech_language

logger = logging.getLogger(__name__)


app = FastAPI(
    title="RetailMate Agent Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# SERVICES
# ============================================================

voice_service = MultilingualTTSService()
agent_workflow = AgentWorkflow()


# ============================================================
# REQUEST SCHEMAS
# ============================================================

class TextToSpeechRequest(BaseModel):
    text: str
    language: str = "en"
    speed: float = 0.95


class AssistantRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    language: str = "en"


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "agent-service"
    }


# ============================================================
# AGENT / ASSISTANT QUERY
# ============================================================

@app.post("/api/assistant/query")
async def assistant_query(request: AssistantRequest):

    if not request.query or not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty."
        )

    request_started = time.perf_counter()
    request_started_at = datetime.now(timezone.utc).isoformat()

    try:
        result = await agent_workflow.process(
            query=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            language=normalize_language(request.language),
        )

        result.setdefault("timing", {})
        result["timing"].update({
            "agent_http_request_start": request_started_at,
            "agent_http_response_end": datetime.now(timezone.utc).isoformat(),
            "agent_http_latency_ms": round(
                (time.perf_counter() - request_started) * 1000,
                2,
            ),
        })

        return result

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


# ============================================================
# TEXT TO SPEECH
# ============================================================

@app.post("/api/voice/tts")
def text_to_speech(request: TextToSpeechRequest):

    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    language = normalize_language(request.language)

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

    request_started = time.perf_counter()
    request_started_at = datetime.now(timezone.utc).isoformat()
    synthesis_started = time.perf_counter()

    try:

        filename = f"tts_{uuid.uuid4().hex}.wav"

        output_path = (
            Path(__file__).resolve().parents[1]
            / "audio"
            / filename
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        result = voice_service.text_to_speech(
            text=request.text,
            language=language,
            output_path=str(output_path),
            speed=request.speed
        )

        complete_at = datetime.now(timezone.utc).isoformat()
        timings = {
            "tts_request_start": request_started_at,
            "tts_first_audio": complete_at,
            "tts_complete": complete_at,
            "tts_time_to_first_audio_ms": round(
                (time.perf_counter() - synthesis_started) * 1000,
                2,
            ),
            "tts_total_ms": round(
                (time.perf_counter() - request_started) * 1000,
                2,
            ),
            "tts_streaming": False,
            "tts_buffering": "complete WAV is generated and written before response",
        }
        logger.info(
            "[Voice Pipeline] TTS: %.2f ms | first_audio=complete_file | streaming=false",
            timings["tts_total_ms"],
        )

        return {
            "success": True,
            "language": language,
            "speech_language": speech_language(language),
            "audio_path": result["audio_path"],
            "sample_rate": result["sample_rate"],
            "audio_url": f"/api/voice/audio/{filename}",
            "timing": timings,
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


@app.post("/api/voice/tts/stream")
def stream_text_to_speech(request: TextToSpeechRequest):
    """Stream Bulbul v3 MP3 chunks without waiting for a complete WAV file."""

    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    language = normalize_language(request.language)
    started = time.perf_counter()

    try:
        chunks = voice_service.stream_audio(
            text=request.text,
            language=language,
            speed=request.speed,
        )

        def timed_chunks():
            first_chunk = True
            for chunk in chunks:
                if first_chunk:
                    logger.info(
                        "[Voice Pipeline] TTS stream first_audio_ms=%.2f",
                        (time.perf_counter() - started) * 1000,
                    )
                    first_chunk = False
                yield chunk

            logger.info(
                "[Voice Pipeline] TTS stream complete_ms=%.2f",
                (time.perf_counter() - started) * 1000,
            )

        return StreamingResponse(
            timed_chunks(),
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "no-store",
                "X-TTS-Streaming": "true",
                "X-TTS-Language": speech_language(language),
            },
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Streaming TTS unavailable")
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ============================================================
# GET GENERATED AUDIO
# ============================================================

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