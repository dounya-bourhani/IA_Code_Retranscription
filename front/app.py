import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text

st.title('Vocal to notebook')

def handle_audio_recording():
    audio = mic_recorder(start_prompt="⏺️ Start recording", stop_prompt="⏹️ Stop recording", key='recorder')
    if audio:
        st.audio(audio['bytes'], format='audio/wav')

def handle_speech_to_text():
    text = speech_to_text(language='fr', start_prompt="Start recording", stop_prompt="Stop recording", just_once=False, key='STT')
    if text:
        st.write("Converted text:", text)

state = st.session_state

if 'text_received' not in state:
    state.text_received = []

st.header("Convert speech to text:")
handle_speech_to_text()

st.header("Record your voice, and play the recorded audio:")
handle_audio_recording()

# Display previously converted texts
if state.text_received:
    st.header("Previously Converted Texts:")
    for text in state.text_received:
        st.text(text)








