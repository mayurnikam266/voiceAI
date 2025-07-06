import streamlit as st
import requests
import tempfile
import os
import time
import pygame
from streamlit_mic_recorder import mic_recorder

st.title("🎙️ Real-Time Voice AI Assistant")

st.markdown("""
**🔐 Enter OpenRouter API Key**  
<small>👉 <a href="" target="_blank" style="color: #1E90FF;">Click here to get your API key</a></small>
""", unsafe_allow_html=True)

api_key = st.text_input("", type="password")

role = st.selectbox("Select Assistant Behavior", ["friendly", "english_tutor", "custom"])
custom_role = st.text_input("Custom Role (if selected above)")

if "stop" not in st.session_state:
    st.session_state.stop = False

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🧠 Reset Memory"):
        requests.post("http://localhost:8000/reset")
        st.success("Memory Cleared")

with col2:
    if st.button("⏹️ Stop Listening"):
        st.session_state.stop = True
        st.warning("Stopped Listening")

mic_audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop", just_once=True, use_container_width=True)

if mic_audio and not st.session_state.stop:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(mic_audio["bytes"])
        tmp_path = tmp.name

    with st.spinner("Thinking..."):
        with open(tmp_path, "rb") as f:
            files = {"audio": f}
            data = {"api_key": api_key, "role": role, "custom_role": custom_role}
            response = requests.post("http://localhost:8000/chat/", files=files, data=data)

        os.remove(tmp_path)

        if response.status_code == 200:
            audio_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            audio_file_path.write(response.content)
            audio_file_path.close()

            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file_path.name)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()  # Unload audio file
            pygame.quit()                # Fully close pygame

            try:
                os.remove(audio_file_path.name)  # Now safe to delete
            except PermissionError:
                st.warning("Audio file was still in use and could not be deleted.")
    
            st.success("✅ AI Replied")

        else:
            st.error("Something went wrong")
