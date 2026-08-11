import os
import logging
import tempfile
import subprocess
import shutil

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


# --- ฟังก์ชันจัดการเสียงและถอดความ ---

def transcribe(audio_path: str) -> str:
    """ฟังก์ชันหลักสำหรับถอดความเสียงเป็นข้อความ"""
    try:
        result = asr.transcribe([audio_path])
        
        if isinstance(result, tuple):
            result = result[0]
            
        if not result or len(result) == 0:
            return ""
            
        text_output = result[0]
        
        if isinstance(text_output, str):
            return text_output
        elif hasattr(text_output, "text"):
            return text_output.text
        elif isinstance(text_output, list) and len(text_output) > 0:
            return str(text_output[0])
        else:
            return str(text_output)
            
    except Exception as exc:
        logger.warning(f"ASR Transcription failed: {exc}")
        return ""


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

# 1. Endpoint สำหรับอัปโหลดไฟล์ (แยกออกมาให้ถูกต้องแล้ว)
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


# 2. Endpoint สำหรับทำ Real-time ผ่าน WebSocket
@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connected for real-time transcription")
    
    # สะสมข้อมูลเสียงที่ส่งมาทีละนิด
    audio_buffer = bytearray()

    try:
        while True:
            # รับข้อมูลจากหน้าเว็บ (รับได้ทั้งข้อความและเสียง)
            message = await websocket.receive()
            
            # ถ้ารับคำสั่ง CLEAR ให้ล้าง Buffer
            if "text" in message and message["text"] == "CLEAR":
                audio_buffer.clear()
                logger.info("Audio buffer cleared by client")
                continue
                
            # ถ้ารับเป็นไฟล์เสียง ให้เอาไปสะสมต่อ
            if "bytes" in message:
                chunk = message["bytes"]
                audio_buffer.extend(chunk)
            else:
                continue # ถ้าไม่ใช่ทั้ง text และ bytes ให้ข้ามไป
            
            # ถ้ามีข้อมูลเสียงแล้ว ค่อยเอาไปแปลงไฟล์
            if len(audio_buffer) > 0:
                temp_in_path = None
                temp_out_path = None
                
                try:
                    # 1. บันทึกเสียงที่รับมาลงไฟล์ชั่วคราวต้นฉบับ
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_in:
                        temp_in.write(audio_buffer)
                        temp_in_path = temp_in.name
                    
                    # 2. ตั้งชื่อไฟล์ปลายทางเป็น .wav
                    temp_out_path = temp_in_path + ".wav"
                    
                    # 3. สั่ง Windows ให้ใช้ FFmpeg แปลงไฟล์ให้เป็น .wav แบบ 16kHz
                    subprocess.run([
                        "ffmpeg.exe", "-y", "-i", temp_in_path, 
                        "-ar", "16000", "-ac", "1", temp_out_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
                    
                    # 4. ส่งไฟล์ .wav ที่บริสุทธิ์ไปให้ AI ถอดความ
                    if os.path.exists(temp_out_path):
                        text = transcribe(temp_out_path)
                        print(f"======== ข้อความที่ AI ได้: '{text}' ========")
                        await websocket.send_json({"text": text})
                    
                except Exception as e:
                    logger.warning(f"Partial transcription error: {e}")
                finally:
                    # ลบไฟล์ชั่วคราวทิ้งเสมอ
                    if temp_in_path and os.path.exists(temp_in_path):
                        os.remove(temp_in_path)
                    if temp_out_path and os.path.exists(temp_out_path):
                        os.remove(temp_out_path)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        audio_buffer.clear()