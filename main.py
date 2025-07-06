from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from stt_engine import transcribe_audio
from ai_engine import call_ai_engine
from tts_engine import speak
from memory_store import memory, reset_memory
import uuid
import os
from starlette.background import BackgroundTask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat/")
async def chat(
    audio: UploadFile = File(...),
    api_key: str = Form(...),
    role: str = Form(...),
    custom_role: str = Form("")
):
    filename = f"audio_{uuid.uuid4()}.wav"
    with open(filename, "wb") as f:
        f.write(await audio.read())

    prompt = transcribe_audio(filename)
    os.remove(filename)

    response = call_ai_engine(prompt, api_key, role, custom_role)
    memory.append({"user": prompt, "assistant": response})

    audio_reply_path = await speak(response)

    def delete_after_send(path):
        try:
            os.remove(path)
        except:
            pass

    return FileResponse(
        audio_reply_path,
        media_type="audio/mpeg",
        background=BackgroundTask(delete_after_send, audio_reply_path)
    )

@app.post("/reset")
def reset():
    reset_memory()
    return JSONResponse({"message": "Memory cleared."})

@app.get("/memory")
def get_memory():
    return memory
