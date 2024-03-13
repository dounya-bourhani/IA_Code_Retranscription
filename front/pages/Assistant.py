import streamlit as st
import speech_recognition as sr

# Function to transcribe speech to text
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
        return text
    except sr.UnknownValueError:
        st.write("Impossible de comprendre l'audio")
        return ""
    except sr.RequestError as e:
        st.write("Erreur lors de la requête à l'API Google : ", e)
        return ""

# Function to save request to history
def save_to_history(request):
    if 'history' not in st.session_state:
        st.session_state['history'] = []
    st.session_state['history'].append(request)

# Function to display history tab
def display_history():
    if 'history' in st.session_state:
        st.subheader("Historique")
        for idx, request in enumerate(st.session_state['history']):
            st.write(f"{idx + 1}. {request}")

def main():
    base = "dark"
    primaryColor = "#0079F7"
    secondaryBackgroundColor = "#25262d"
    font = "monospace"

    st.set_page_config(
        page_title="Voice-to-text",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Application voice-to-text Notebook Assistant")

    # Organize layout with columns and rows
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Enregistrement voix")
        if st.button("🎙️ Générer une requête"):
            text = transcribe_speech()
            save_to_history(text)

    with col2:
        st.subheader("Requête Ecrit")
        text_input = st.text_area("Insérer du texte ici :", "")
        if st.button("Envoyer"):
            if text_input:
                st.write("Texte inséré :", text_input)
                save_to_history(text_input)

    # Display history below the columns
    display_history()

if __name__ == "__main__":
    main()
