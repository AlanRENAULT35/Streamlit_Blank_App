import streamlit as st
import openai
import requests
from io import BytesIO
from PIL import Image
import base64

# Set your OpenAI API key
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Clé API OpenAI introuvable. Veuillez la définir dans les secrets Streamlit.")
    st.stop()

st.set_page_config(layout="wide", page_title="Prototypage de Jeu Vidéo par IA")

def generate_game_idea(genre, mood, keywords):
    """Génère un titre de jeu, un genre et un résumé à l'aide de GPT-4o."""
    # Rendre le prompt plus strict pour s'assurer que les étiquettes (Title:, Genre:, Summary:) sont toujours présentes
    prompt = f"""Proposez une idée de jeu vidéo innovante. Le jeu doit être un jeu de {genre}, avec une atmosphère {mood}. Incorporez les mots-clés suivants : {keywords}.
    
    Veuillez formater votre réponse comme suit :
    Title: [Votre titre de jeu ici]
    Genre: [Votre genre de jeu ici]
    Summary: [Votre résumé concis (environ 100-150 mots) ici]
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Vous êtes un assistant créatif de concepteur de jeux. Votre objectif est de générer des concepts de jeu clairs et formatés précisément."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400, # Augmenter les tokens pour s'assurer que le résumé est complet
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erreur lors de la génération de l'idée de jeu : {e}")
        return None

def generate_image_from_text(prompt_text):
    """Génère une image à l'aide de DALL-E 3."""
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=f"Pochette de jeu vidéo : {prompt_text}",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Erreur lors de la génération de l'image : {e}")
        return None

def generate_speech_from_text(text_to_speak):
    """Génère de l'audio à partir du texte à l'aide de l'API OpenAI TTS."""
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=text_to_speak
        )
        return response.content
    except Exception as e:
        st.error(f"Erreur lors de la génération de la parole : {e}")
        return None

def display_image_from_url(url):
    """Affiche une image à partir d'une URL."""
    if url:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            st.image(img, caption="Pochette du jeu", use_container_width=True)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            href = f'<a href="data:file/png;base64,{img_str}" download="pochette_jeu.png">Télécharger l\'image</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erreur lors de l'affichage de l'image : {e}")

def transcribe_audio(audio_file):
    """Espace réservé pour la transcription de l'API Whisper."""
    st.info("L'intégration de l'API Whisper est un espace réservé.")
    return "Transcription de l'audio (espace réservé)."

def fine_tune_model(training_file_id):
    """Espace réservé pour l'API de Fine-tuning d'OpenAI."""
    st.info("L'intégration de l'API de Fine-tuning est un espace réservé.")
    return f"Le Fine-tuning n'est pas implémenté pour l'ID de fichier : {training_file_id}."

## Interface utilisateur Streamlit ##
st.title("🎮 Prototypage de Jeu Vidéo par IA")

st.markdown("""
Cette application vous aide à prototyper des idées de jeux vidéo en utilisant les puissantes API d'OpenAI.
Générez des concepts de jeu avec GPT, créez de superbes pochettes avec DALL-E, et écoutez le résumé du jeu grâce à la synthèse vocale.
""")

### 💡 Génération d'Idée de Jeu, d'Image et de Synthèse Vocale (GPT, DALL-E, TTS)

st.header("1. Générer une Idée de Jeu, une Image et un Résumé Vocal")
col1, col2 = st.columns(2)

with col1:
    selected_genre = st.selectbox(
        "Sélectionnez un Genre :",
        ["Action", "Aventure", "RPG", "Stratégie", "Simulation", "Puzzle", "Horreur", "Sci-Fi", "Fantasy", "Sports"]
    )
    selected_mood = st.selectbox(
        "Sélectionnez une Ambiance :",
        ["Épique", "Mystérieuse", "Humoristique", "Sombre", "Légère", "Brute", "Futuriste", "Historique", "Confortable"]
    )
    keywords_input = st.text_input(
        "Entrez des Mots-clés (séparés par des virgules) :",
        "magie, ruines antiques, héros courageux"
    )

generate_all_button = st.button("Générer le Concept de Jeu, l'Image et le Résumé Vocal")

if generate_all_button:
    if selected_genre and selected_mood and keywords_input:
        with st.spinner("Génération du concept de jeu, de l'image et du résumé vocal..."):
            # 1. Génération de l'idée de jeu (GPT)
            game_concept_raw = generate_game_idea(selected_genre, selected_mood, keywords_input)

            if game_concept_raw:
                # Initialiser les variables pour le concept de jeu
                game_title = "N/A"
                game_genre = "N/A"
                game_summary = "Aucun résumé généré."

                # Analyse améliorée du texte généré par GPT
                for line in game_concept_raw.split('\n'):
                    if line.strip().startswith("Title:"):
                        game_title = line.replace("Title:", "").strip()
                    elif line.strip().startswith("Genre:"):
                        game_genre = line.replace("Genre:", "").strip()
                    elif line.strip().startswith("Summary:"):
                        game_summary = line.replace("Summary:", "").strip()

                # Stocker dans session_state
                st.session_state.game_title = game_title
                st.session_state.game_genre = game_genre
                st.session_state.game_summary = game_summary

                st.subheader("Concept de Jeu Généré :")
                st.write(f"**Titre :** {st.session_state.game_title}")
                st.write(f"**Genre :** {st.session_state.game_genre}") # Affichage unique du genre
                st.write(f"**Résumé :** {st.session_state.game_summary}")

                # 2. Génération de l'image (DALL-E)
                # Utiliser le titre et le résumé extraits pour le prompt de l'image
                image_prompt_for_dalle = f"Pochette de jeu vidéo pour un jeu de {st.session_state.game_genre} intitulé '{st.session_state.game_title}'. Représentez le thème : {st.session_state.game_summary}"
                st.info(f"Génération de l'image avec le prompt : '{image_prompt_for_dalle}'")
                image_url = generate_image_from_text(image_prompt_for_dalle)
                if image_url:
                    st.session_state.generated_image_url = image_url
                    st.subheader("Pochette Générée :")
                    display_image_from_url(st.session_state.generated_image_url)

                # 3. Génération de la synthèse vocale (TTS) pour le résumé
                if st.session_state.game_summary and st.session_state.game_summary != "Aucun résumé généré.":
                    st.subheader("Résumé Vocal :")
                    audio_bytes = generate_speech_from_text(st.session_state.game_summary)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mpeg")
                else:
                    st.warning("Impossible de générer le résumé vocal car le résumé du jeu est vide ou non généré.")
            else:
                st.error("La génération du concept de jeu a échoué.")
    else:
        st.warning("Veuillez sélectionner un genre, une ambiance et entrer des mots-clés.")

st.markdown("---")
st.markdown("Construit avec ❤️ et les API OpenAI par Alan RENAULT")
