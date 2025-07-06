import edge_tts
import uuid
import os

async def speak(text: str) -> str:
    output_file = f"tts_{uuid.uuid4()}.mp3"
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save(output_file)
    return output_file
