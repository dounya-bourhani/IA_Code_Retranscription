import streamlit as st

## sidebar token insert
def submit_path():
    if "path" not in st.session_state:
            st.session_state.path = ""
    if st.session_state.path_input:
        st.session_state.path = st.session_state.path_input
        st.session_state.path_input = ""

def submit_token():
    if "token" not in st.session_state:
            st.session_state.token = ""
    if st.session_state.token_input:
        st.session_state.token = st.session_state.token_input
        st.session_state.token_input = ""


st.set_page_config(
        page_title="Speech-to-text",
        page_icon="🔗",
        layout="wide",
    )


st.subheader("Connecter votre notebook")
st.text_input("", key="path_input", on_change=submit_path, placeholder= "Insérez votre chemin ici")
st.button("Connecter", on_click=submit_path)
if "path" in st.session_state: 
    st.write("✅ Chemin activé")
    st.write(f"Directory : {st.session_state.path}")