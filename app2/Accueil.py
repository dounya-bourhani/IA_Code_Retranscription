import streamlit as st

def main():
    st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Speech-to-text Notebook Assistant")

    st.header("Bienvenue sur Code Generation Assistant")

    
    st.write("""L'application Code Generation est un outil innovant conçu pour aider les développeurs à générer du code rapidement et efficacement en utilisant un assistant virtuel.""")
    
    col1, col2 = st.columns(2)
    
    st.write("""les utilisateurs peuvent interagir avec l'assistant pour exprimer leurs besoins en matière de code.""")

if __name__ == "__main__":
    main()
