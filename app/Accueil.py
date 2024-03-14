import streamlit as st



def main():
    base = "dark"
    primaryColor = "#0079F7"
    secondaryBackgroundColor = "#25262d"
    font = "monospace"

    st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Speech-to-text Notebook Assistant")

    st.header("Bienvenue sur Code Generation Assistant")

    st.sidebar.success("Sélectionner une page")

    st.write("""L'application Code Generation est un outil innovant conçu pour aider les développeurs à générer du code rapidement et efficacement en utilisant un assistant virtuel.""")
    
    col1, col2 = st.columns(2)

    with col1:
       st.image("app/icons/typing.jpg", width=500)
       st.write("""Que ce soit par le biais de requêtes textuelles écrites à la main...""")
    
    with col2:
       st.image("app/icons/reco_vocale.jpg", width=500)
       st.write("""ou de requêtes détectées par reconnaissance vocale...""")
                 
    st.write("""les utilisateurs peuvent interagir avec l'assistant pour 
             exprimer leurs besoins en matière de code.""")



    # Define values 
    if 'path' not in st.session_state:
            st.session_state['path'] = ""
    if 'file' not in st.session_state:
            st.session_state['file'] = ""

    
if __name__ == "__main__":
    main()
