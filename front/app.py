import streamlit as st
import speech_recognition as sr

def transcribe_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        st.write("Dites quelque chose...")
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.listen(source)

    try:
        st.write("Analyse de l'audio...")
        text = recognizer.recognize_google(audio_data, language='fr-FR')
        st.write("Vous avez dit : ", text)
    except sr.UnknownValueError:
        st.write("Impossible de comprendre l'audio")
    except sr.RequestError as e:
        st.write("Erreur lors de la requête à l'API Google : ", e)

def main():
    st.title("Application de transcription de la parole")

    if st.button("Commencer l'enregistrement"):
        transcribe_speech()

if __name__ == "__main__":
    main()
