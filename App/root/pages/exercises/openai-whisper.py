import streamlit as st
from openai import OpenAI
import os

# --- Configuration ---
# Load OpenAI API key from Streamlit's secrets
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. Please add it to .streamlit/secrets.toml")
    st.stop() # Stop the app if the key is not found

client = OpenAI(api_key=OPENAI_API_KEY)

# --- 1. Créer une méthode openai_transcribe ---
def openai_transcribe(audio_file_path: str) -> str:
    """
    Transcribes an audio file using OpenAI Whisper.

    Args:
        audio_file_path: The path to the audio file.

    Returns:
        The transcribed text.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        st.error(f"Error during transcription: {e}")
        return ""

# --- 2. Créer une méthode openai_translate ---
def openai_translate(audio_file_path: str) -> str:
    """
    Translates an audio file into English using OpenAI Whisper.

    Args:
        audio_file_path: The path to the audio file.

    Returns:
        The translated text (in English).
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            translation = client.audio.translations.create(
                model="whisper-1",
                file=audio_file
            )
        return translation.text
    except Exception as e:
        st.error(f"Error during translation: {e}")
        return ""

# --- 3. Créer une méthode text_to_speech ---
def text_to_speech(text: str, output_audio_path: str = "output.mp3"):
    """
    Converts text to speech using OpenAI's Text-to-Speech model.

    Args:
        text: The text to convert.
        output_audio_path: The path to save the generated audio file.
    """
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy", # You can choose other voices like 'nova', 'shimmer', 'echo', 'fable', 'onyx'
            input=text,
        )
        response.stream_to_file(output_audio_path)
        st.success(f"Text-to-speech audio saved to {output_audio_path}")
        return output_audio_path
    except Exception as e:
        st.error(f"Error during text-to-speech conversion: {e}")
        return None

# --- 4. Ajouter une page 'Transcription' à votre application Streamlit ---

st.set_page_config(page_title="Audio Processing App", layout="centered")

st.title("Audio Processing with OpenAI")

# Navigation (optional for a single-page app, but good practice for multi-page)
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Transcription & Translation", "Text-to-Speech"])

if page == "Transcription & Translation":
    st.header("Transcription & Translation")
    st.write("Upload an audio file to transcribe it or translate it to English.")

    uploaded_file = st.file_uploader("Choose an audio file...", type=["mp3", "wav", "m4a", "ogg", "flac"])

    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open(os.path.join("temp_audio", uploaded_file.name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        audio_path = os.path.join("temp_audio", uploaded_file.name)

        st.audio(uploaded_file, format=uploaded_file.type)

        if st.button("Transcribe"):
            with st.spinner("Transcribing..."):
                transcribed_text = openai_transcribe(audio_path)
            if transcribed_text:
                st.subheader("Transcription:")
                st.info(transcribed_text)

        if st.button("Translate to English"):
            with st.spinner("Translating..."):
                translated_text = openai_translate(audio_path)
            if translated_text:
                st.subheader("Translation (English):")
                st.info(translated_text)

        # Clean up the temporary file
        os.remove(audio_path)

        # Ensure temp_audio directory is removed if empty (optional)
        if not os.listdir("temp_audio"):
            os.rmdir("temp_audio")

elif page == "Text-to-Speech":
    st.header("Text-to-Speech")
    st.write("Enter text to convert it into an audio file.")

    input_text = st.text_area("Enter text here:", height=200)

    if st.button("Generate Audio"):
        if input_text:
            with st.spinner("Generating audio..."):
                output_audio_file = text_to_speech(input_text)
            if output_audio_file:
                st.subheader("Generated Audio:")
                st.audio(output_audio_file)
                # Option to download
                with open(output_audio_file, "rb") as file:
                    btn = st.download_button(
                        label="Download Audio",
                        data=file,
                        file_name="generated_audio.mp3",
                        mime="audio/mp3"
                    )
                os.remove(output_audio_file) # Clean up generated file
        else:
            st.warning("Please enter some text to generate audio.")

# Create a temporary directory if it doesn't exist
if not os.path.exists("temp_audio"):
    os.makedirs("temp_audio")