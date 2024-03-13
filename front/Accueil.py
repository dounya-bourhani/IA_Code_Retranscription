import streamlit as st


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

if __name__ == "__main__":
    main()
