import streamlit as st
import speech_recognition as sr
import pyperclip
from langchain.llms import HuggingFaceHub
from JupyCoder_lib2 import JupyCoder

##################################### FONCTIONS ##########################################



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

def display_history():
    if 'history' in st.session_state:
        # Create a horizontal layout
        header_col, download_col = st.columns([9.7,3])

        # Display the "Historique" title
        with header_col:
            st.subheader("Historique :")

        # Display the download button in the right column
        with download_col:
            download_history()

        # Reverse the order of the history list
        reversed_history = reversed(st.session_state['history'])
        for idx, request in enumerate(reversed_history):
            # Use columns to align the copy button to the right side
            col1, col2 = st.columns([10, 1.1])
            # Display the request
            col1.write(f"- {request}")
            # Add a button to copy the request to clipboard
            if col2.button(f"Copier", key=f"copy_button_{idx}"):
                pyperclip.copy(request)

def download_history():
    if 'history' in st.session_state:
        # Get the reversed history
        history = st.session_state['history']
        # Create a string with the reversed history
        history_str = '\n'.join(history)
        # Prompt the user to download the history as a text file
        st.download_button(
            label="Télécharger l'historique",
            data=history_str,
            file_name='history.txt',
            mime='text/plain',
        )

##################################### PAGE ##########################################
                
def assistant():
    st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🎙️",
        layout="wide",
    )
    
    ## sidebar token insert
    def submit_token():
        if "token" not in st.session_state:
                st.session_state.token = ""
        if st.session_state.token_input:
            st.session_state.token = st.session_state.token_input

    if "token" not in st.session_state:
        st.session_state.token = ""

    st.sidebar.text_input("Insérer un token Hugging Face 🤗 :", key="token_input", on_change=submit_token, type = 'password')
    
    st.sidebar.button("Valider", on_click=submit_token)

    if len(st.session_state.token) > 2:
        st.sidebar.write("✅ Token activé")
        llm =  HuggingFaceHub(repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1", 
                                huggingfacehub_api_token=st.session_state.token,
                                model_kwargs={"temperature": 0.1, "max_new_tokens": 500})
    
        JupyAgent = JupyCoder(st.session_state.path, 
                          llm)
        
    

    ## Chatbot
    if 'path' not in st.session_state:
            st.header("👈 Merci de vous connecter à un notebook en cliquant sur l'onglet 'Connexion avec notebook'")
    else:
        st.title("Speech-to-text Notebook Assistant")

        # Organize layout with columns and rows
        col1, col2 = st.columns([2, 4])

        with col1:
            st.subheader("Enregistrement voix")
            if st.button("🎙️ Enregistrer"):
                text = transcribe_speech()
                JupyAgent.make_action(text)
                save_to_history(text)


        with col2:
            if "my_text" not in st.session_state:
                    st.session_state.my_text = ""
            col2a, col2b = st.columns([3, 2])
            with col2a:
                st.subheader("Ecrire une requête")
            with col2b:
                def clear():
                    st.session_state.widget = ""
                st.button("Effacer 🗑️", on_click=clear)

            def submit():
                if st.session_state.widget:
                    st.session_state.my_text = st.session_state.widget
                    save_to_history(st.session_state.my_text)
            with st.form("my_form"):
                text_input = st.text_input("Insérez du texte ici :", key="widget")
                button_clicked = st.form_submit_button("Envoyer")
                submit()
            
            if len(text_input) > 3 and button_clicked:
                print("send")
                JupyAgent.make_action(text_input)

            
        # Display history below the columns
        display_history()



assistant()
