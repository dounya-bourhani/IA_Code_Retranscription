import streamlit as st
import speech_recognition as sr
import os

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
    if request:
        st.session_state['history'].append(request)

# Function to display history tab
def display_history():
    if 'history' in st.session_state:
        st.subheader("Historique")
        # Reverse the order of the history list
        reversed_history = reversed(st.session_state['history'])
        for idx, request in enumerate(reversed_history):
            st.write(f"- {request}")


# Définition d'un composant personnalisé pour récupérer le chemin complet d'un fichier
def file_path_uploader(label, file_types=".ipynb"):
    """
    Affiche un file_uploader et retourne le chemin du fichier sélectionné.
    """
    file = st.file_uploader(label, type=file_types)
    if file is not None:
        return file.name, file
    return None, None




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


    ######
    st.title("Application voice-to-text Notebook Assistant")


    # Utilisation du composant personnalisé
    file_name, file_content = file_path_uploader("Sélectionnez un fichier")

    # Affichage du chemin complet du fichier
    if file_content is not None:
        st.write("Chemin complet du fichier:", os.path.abspath(file_name))



    # Organize layout with columns and rows
    col1, col2 = st.columns([2, 4])

    with col1:
        st.subheader("Enregistrement voix")
        if st.button("🎙️ Générer une requête"):
            text = transcribe_speech()
            save_to_history(text)

    with col2:
        if "my_text" not in st.session_state:
                st.session_state.my_text = ""

        def submit():
            st.session_state.my_text = st.session_state.widget
            st.session_state.widget = ""

        st.text_input("Enter text here", key="widget", on_change=submit)
        st.button("Submit", on_click=submit)

        my_text = st.session_state.my_text
        save_to_history(my_text)
    
    # Display history below the columns
    display_history()

if __name__ == "__main__":
    main()
