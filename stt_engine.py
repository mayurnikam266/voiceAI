from faster_whisper import WhisperModel

model = None

def transcribe_audio(audio_path: str) -> str:
    global model
    if model is None:
        model = WhisperModel("base")
    segments, _ = model.transcribe(audio_path)
    return " ".join([seg.text for seg in segments]).strip()
