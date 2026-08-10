import os
import logging
import tempfile

import torch
import torchaudio
import soundfile as sf
import numpy as np
import nemo.collections.asr as nemo_asr

from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Loads .env from the current working directory
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-voice-app")

# CORS: comma-separated list of origins in ALLOWED_ORIGINS
_allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = (
    ["*"] if _allowed_origins.strip() == "*"
    else [o.strip() for o in _allowed_origins.split(",") if o.strip()]
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
MODEL_REPO_ID = os.environ.get("MODEL_REPO_ID")
MODEL_FILENAME = os.environ.get("MODEL_FILENAME")

logger.info("Downloading model %s / %s ...", MODEL_REPO_ID, MODEL_FILENAME)
local_path = hf_hub_download(
    repo_id=MODEL_REPO_ID,
    filename=MODEL_FILENAME,
    repo_type="model",
)

asr = nemo_asr.models.EncDecRNNTBPEModel.restore_from(local_path)
asr.eval()
device = "cuda" if torch.cuda.is_available() else "cpu"
asr = asr.to(device)
logger.info("Model loaded on device: %s", device)


# --- ฟังก์ชันจัดการเสียงและถอดความ (เหมือนเดิม) ---

def _load_audio(audio_path: str):
    """Load audio robustly. Fall back to soundfile if torchaudio fails."""
    try:
        wav, sr = torchaudio.load(audio_path)
    except Exception as exc:
        logger.warning("torchaudio.load failed (%s), falling back to soundfile", exc)
        data, sr = sf.read(audio_path, dtype="float32", always_2d=True)
        wav = torch.from_numpy(np.ascontiguousarray(data.T))
    return wav, sr


def transcribe(audio_path: str) -> str:
    wav, sr = _load_audio(audio_path)

    if sr != 16000:
        wav = torchaudio.functional.resample(wav, sr, 16000)

    if wav.shape[0] > 1:
        wav = wav.mean(dim=0, keepdim=True)

    with torch.no_grad():
        logits, logits_len, _ = asr.forward(
            input_signal=wav.to(device),
            input_signal_length=torch.tensor(
                [wav.shape[1]],
                device=device
            )
        )
        preds = asr.decoding.decode(
            logits,
            logits_len
        )

    if not preds:
        return ""

    result = preds[0]
    return result.text if hasattr(result, "text") else result


# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "AI Voice App Backend is running!", "model_status": "loaded"}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": device,
        "model_loaded": asr is not None,
    }

# 1. Endpoint สำหรับอัปโหลดไฟล์ (แบบเก่า)[cite: 1]
@app.post("/transcribe")
async def transcribe_api(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    suffix = os.path.splitext(audio.filename)[1] or ".wav"
    temp_path = None
    try:
        contents = await audio.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(contents)
            temp_path = temp.name

        text = transcribe(temp_path)
        return {"text": text}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Transcription failed")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# 2. Endpoint ใหม่ สำหรับทำ Real-time ผ่าน WebSocket
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected for real-time transcription")
    
    # สะสมข้อมูลเสียงที่ส่งมาทีละนิด
    audio_buffer = bytearray()

    try:
        while True:
            # รับข้อมูลเสียงจากหน้าบ้าน (Frontend ต้องส่งเป็น Raw Bytes)
            chunk = await websocket.receive_bytes()
            audio_buffer.extend(chunk)
            
            temp_path = None
            try:
                # บันทึก buffer ปัจจุบันลงไฟล์ชั่วคราวเพื่อนำไปให้โมเดลอ่าน
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
                    temp.write(audio_buffer)
                    temp_path = temp.name
                
                # ถอดความข้อความจากเสียงที่สะสมไว้ทั้งหมด
                text = transcribe(temp_path)
                
                # ส่งข้อความกลับไปที่ Frontend
                await websocket.send_json({"text": text})
                
            except Exception as e:
                logger.warning(f"Partial transcription error (waiting for more data): {e}")
            finally:
                # ลบไฟล์ชั่วคราวทิ้งทุกครั้งที่ประมวลผลเสร็จในรอบนั้นๆ
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        # เมื่อผู้ใช้กดปิดไมค์หรือปิดเว็บ ให้ล้าง Buffer
        audio_buffer.clear()