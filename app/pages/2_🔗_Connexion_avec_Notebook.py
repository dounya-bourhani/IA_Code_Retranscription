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

##################################### PAGES ##########################################

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

##################################### PAGES ##########################################
st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🔗",
        layout="wide",
    )

st.title("Connexion avec Notebook")

file_con()
