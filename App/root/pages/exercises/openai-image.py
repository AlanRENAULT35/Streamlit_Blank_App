import streamlit as st
from openai import OpenAI
import base64

# --- Configuration ---
# Use st.secrets to securely access your OpenAI API key
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("OpenAI API key not found in Streamlit secrets. "
             "Please add it to your .streamlit/secrets.toml file like: "
             "OPENAI_API_KEY = 'YOUR_API_KEY'")
    st.stop() # Stop the app if the key is not found

# Initialize the OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 1. Création de méthodes pour DALL-E ---

def openai_create_image(prompt: str) -> str:
    """
    This method should take a text prompt as input and use the DALL-E API from OpenAI
    to generate an image based on the provided prompt. The generated image should be
    returned as output of the method.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",  # Or "dall-e-2" if you prefer
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image with DALL-E: {e}")
        return None

def openai_create_image_variation(image_path: str, prompt: str) -> str:
    """
    This method should take an existing image and a text prompt as input and use
    the DALL-E API from OpenAI to create a variation of the image based on the prompt.
    The image variation should be returned as output of the method.
    
    Note: DALL-E 3 does not support image variations directly from an image.
    This functionality is typically available with DALL-E 2.
    For DALL-E 3, you would typically regenerate from a new prompt or modify the existing one.
    This implementation uses DALL-E 2 for variation.
    The 'image_path' should be a path to a local image file.
    """
    try:
        # For variations, DALL-E 2 is used and requires the image to be in a specific format
        # and size. It's often easier to work with local files for this.
        with open(image_path, "rb") as image_file:
            response = client.images.generate_variation(
                image=image_file,
                model="dall-e-2",
                n=1,
                size="1024x1024"
            )
            image_url = response.data[0].url
            return image_url
    except Exception as e:
        st.error(f"Error creating image variation with DALL-E 2: {e}")
        return None

# --- 2. Connexion à l'API ChatGPT ---

def generate_prompt_with_chatgpt(user_text: str) -> str:
    """
    This method should take text provided by the user as input and use the ChatGPT API
    to generate an improved text prompt based on the provided text. The improved prompt
    should be returned as output of the method.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or "gpt-4o", "gpt-4", etc.
            messages=[
                {"role": "system", "content": "You are a helpful assistant that improves image generation prompts. Make them more descriptive and creative for DALL-E."},
                {"role": "user", "content": f"Improve this prompt for DALL-E: '{user_text}'"}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        improved_prompt = response.choices[0].message.content.strip()
        return improved_prompt
    except Exception as e:
        st.error(f"Error generating improved prompt with ChatGPT: {e}")
        return None

# --- 3. Intégration à l'application web Streamlit ---

st.set_page_config(page_title="DALL-E Image Generator", layout="centered")

st.title("🎨 DALL-E Image Generator")
st.markdown("Generate images from text using OpenAI's DALL-E API.")

# DALL-E Image Generation Section
st.header("🖼️ Generate Image from Text")
user_input_dalle = st.text_area("Enter a text description for your image:", "A futuristic city at sunset, with flying cars and towering skyscrapers, in a vibrant cyberpunk style.")

if st.button("Generate Image"):
    if user_input_dalle:
        st.info("Generating your image... This may take a moment.")
        with st.spinner('Thinking...'):
            image_url = openai_create_image(user_input_dalle)
            if image_url:
                st.success("Image generated successfully!")
                st.image(image_url, caption=user_input_dalle, use_column_width=True)
                st.write(f"[Download Image]({image_url})")
            else:
                st.error("Failed to generate image.")
    else:
        st.warning("Please enter a description to generate an image.")

st.markdown("---")

# ChatGPT Prompt Improvement Section
st.header("✨ Improve Your Prompt with ChatGPT")
user_input_chatgpt = st.text_area("Enter a draft prompt to get an improved version:", "cat sitting on a couch")

if st.button("Improve Prompt"):
    if user_input_chatgpt:
        st.info("Improving your prompt with ChatGPT...")
        with st.spinner('Improving...'):
            improved_prompt = generate_prompt_with_chatgpt(user_input_chatgpt)
            if improved_prompt:
                st.success("Prompt improved!")
                st.code(improved_prompt, language="text")
                st.markdown(f"You can now use this improved prompt: **{improved_prompt}**")
            else:
                st.error("Failed to improve prompt.")
    else:
        st.warning("Please enter a prompt to improve.")

st.markdown("---")

# DALL-E Image Variation Section (Requires DALL-E 2 and local file upload)
st.header("🔄 Create Image Variation (DALL-E 2)")
st.info("This feature uses DALL-E 2 and requires you to upload an image. DALL-E 3 does not support direct image variations.")

uploaded_file = st.file_uploader("Upload an image for variation (PNG or JPG recommended):", type=["png", "jpg", "jpeg"])
variation_prompt = st.text_input("Enter a prompt to guide the variation (optional):", "Add a touch of magic to it.")

if st.button("Create Variation"):
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with open("temp_image_for_variation.png", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.info("Creating image variation... This may take a moment.")
        with st.spinner('Varying...'):
            # The prompt for variation in DALL-E 2 is more for guiding the style, not adding new elements directly
            # For simplicity, we are passing it, but its impact on variation is less direct than primary generation.
            variation_image_url = openai_create_image_variation("temp_image_for_variation.png", variation_prompt)
            
            if variation_image_url:
                st.success("Image variation created successfully!")
                st.image(variation_image_url, caption="Image Variation", use_column_width=True)
                st.write(f"[Download Variation]({variation_image_url})")
            else:
                st.error("Failed to create image variation.")
        
        # Clean up the temporary file
        import os
        os.remove("temp_image_for_variation.png")
    else:
        st.warning("Please upload an image to create a variation.")

st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and OpenAI APIs.")

# To run this Streamlit app:
# 1. Save the code as a Python file (e.g., `app.py`).
# 2. Make sure you have the .streamlit/secrets.toml file configured as described above.
# 3. Install the necessary libraries: `pip install streamlit openai`
# 4. Run from your terminal: `streamlit run app.py`

import os

class VisionProcessor:
    def __init__(self):
        # Initialize OpenAI client with API key from environment variable
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def encode_image(self, image_path):
        """Encodes an image to a base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def vision_analyze_image(self, image_input, detail="auto", custom_prompt=None):
        """
        Analyzes an image using OpenAI's Vision model.

        Args:
            image_input (str or bytes): Path to the image file or base64 encoded image string.
            detail (str): Optional. Controls the level of detail in the response.
                          Can be "low", "high", or "auto". Defaults to "auto".
            custom_prompt (str): Optional. A custom prompt to guide the analysis.
                                 If None, a default prompt is used.

        Returns:
            dict: The JSON response from the OpenAI API containing the analysis.
                  Returns None if an error occurs.
        """
        if isinstance(image_input, str) and os.path.exists(image_input):
            # If it's a file path, encode it
            base64_image = self.encode_image(image_input)
        elif isinstance(image_input, str) and image_input.startswith("data:image"):
            # If it's already a data URI (base64 string with header)
            base64_image = image_input.split(",")[1]
        elif isinstance(image_input, bytes):
            # If it's raw bytes (e.g., from st.file_uploader), encode it
            base64_image = base64.b64encode(image_input).decode("utf-8")
        else:
            st.error("Invalid image input. Please provide a file path or image bytes.")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.client.api_key}"
        }

        # Determine the content for the image
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": detail  # Apply detail option
            }
        }

        # Determine the prompt to use
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": custom_prompt if custom_prompt else "What’s in this image? Describe it in detail, including objects, colors, and any discernible text."},
                    image_content
                ],
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use gpt-4o for image understanding
                messages=messages,
                max_tokens=1000,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"An error occurred during image analysis: {e}")
            return None

# --- Streamlit Application ---

st.set_page_config(layout="wide", page_title="Image Analysis with OpenAI Vision")

st.title("👁️ Image Analysis with OpenAI Vision")
st.write("Upload an image and let OpenAI's `gpt-4o` model describe it for you.")

# Initialize VisionProcessor
vision_processor = VisionProcessor()

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
    st.write("")
    st.subheader("Analysis Options")

    # Optional parameters
    detail_option = st.selectbox(
        "Select analysis detail:",
        ("auto", "low", "high"),
        index=0,
        help="Controls the level of detail the model provides. 'Low' is faster and cheaper."
    )

    custom_prompt_input = st.text_area(
        "Enter a custom prompt (optional):",
        value="Describe this image comprehensively, identifying all objects, actions, and any text present.",
        help="Provide specific instructions for the AI on what to focus on in the image."
    )

    if st.button("Analyze Image"):
        with st.spinner("Analyzing image... This may take a moment."):
            # Pass the raw bytes of the uploaded file
            analysis_result = vision_processor.vision_analyze_image(
                uploaded_file.read(),
                detail=detail_option,
                custom_prompt=custom_prompt_input
            )

        if analysis_result:
            st.subheader("Analysis Result:")
            st.markdown(f"**Description:**\n{analysis_result}")
        else:
            st.error("Could not get a valid analysis from the model.")

st.markdown("""
<style>
.stButton>button {
    background-color: #4CAF50;
    color: white;
    font-size: 16px;
    padding: 10px 24px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)
