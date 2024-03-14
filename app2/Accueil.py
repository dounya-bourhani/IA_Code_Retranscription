import streamlit as st

def main():
    st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🎙️",
        layout="wide",
    )

    st.title("Speech-to-text Notebook Assistant")

    st.header("Bienvenue sur Code Generation Assistant")

    ## sidebar token insert
    def submit_token():
        if "token" not in st.session_state:
                st.session_state.token = ""
        if st.session_state.token_input:
            st.session_state.token = st.session_state.token_input
            st.session_state.token_input = ""

    #st.sidebar.text_input("Insérer un token Hugging Face 🤗 :", key="token_input", type='password')
    st.sidebar.text_input("Insérer un token Hugging Face 🤗 :", key="token_input", on_change=submit_token, type = 'password')
    st.sidebar.button("Valider", on_click=submit_token)
    if "token" in st.session_state: 
        st.sidebar.write("✅ Token activé")
    


    st.write("""L'application Code Generation est un outil innovant conçu pour aider les développeurs à générer du code rapidement et efficacement en utilisant un assistant virtuel.""")
    
    col1, col2 = st.columns(2)
    
    st.write("""les utilisateurs peuvent interagir avec l'assistant pour exprimer leurs besoins en matière de code.""")

if __name__ == "__main__":
    main()
