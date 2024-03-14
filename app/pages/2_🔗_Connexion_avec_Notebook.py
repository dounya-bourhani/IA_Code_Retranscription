import streamlit as st
import os

##################################### Functions ##########################################
def file_path_uploader(label, file_types=".ipynb"):
    """
    Affiche un file_uploader et retourne le chemin du fichier sélectionné.
    """
    file = st.file_uploader(label, type=file_types)
    if file is not None:
        return file.name, file
    return None, None

def submit_token():
    if "token" not in st.session_state:
            st.session_state.token = ""
    if st.session_state.token_input:
        st.session_state.token = st.session_state.token_input
        st.session_state.token_input = ""
##################################### PAGES ##########################################
st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🔗",
        layout="wide",
    )


st.sidebar.text_input("Insérer un token Hugging Face 🤗 :", key="token_input", on_change=submit_token, type = 'password')
st.sidebar.button("Valider", on_click=submit_token)
if "token" in st.session_state: 
    st.sidebar.write("✅ Token activé")

def file_con():
    # Utilisation du composant personnalisé
    file_name, file_content = file_path_uploader("Sélectionnez un notebook (.ipynb) :")
    if file_name is None:
        st.write("🔴 Aucun notebook connecté")
    else:
        # Affichage du chemin complet du fichier
        st.write(f"✅ Connexion établie avec notebook '{file_name}'.") 
        path = os.path.abspath(file_name)
        st.write("Chemin : ", path)
        # Ajoute au session_state
        st.session_state['path'] = path
        st.session_state['file'] = file_name


st.title("Connexion avec Notebook")

# Check if the file name is stored in the session state
if 'file' in st.session_state:
    st.write(f"✅ Connexion établie avec notebook '{st.session_state['file']}'.") 
    path = os.path.abspath(st.session_state['file'])
    st.write("Chemin : ", path)
    if st.button("Connecter à un autre notebook"):
        st.session_state.pop('file', None)
        st.session_state.pop('path', None)
        file_con()
else:
    file_con()
