import streamlit as st
from openai import OpenAI
import base64
import os # Import os for file operations and environment variables

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

# --- Vision Method Class ---
class VisionProcessor:
    def __init__(self, openai_client):
        # Initialize OpenAI client passed from the main app
        self.client = openai_client

    def encode_image(self, image_bytes):
        """Encodes image bytes to a base64 string."""
        return base64.b64encode(image_bytes).decode("utf-8")

    def vision_analyze_image(self, image_input_bytes, detail="auto", custom_prompt=None):
        """
        Analyzes an image using OpenAI's Vision model.

        Args:
            image_input_bytes (bytes): Raw bytes of the image file (e.g., from st.file_uploader).
            detail (str): Optional. Controls the level of detail in the response.
                          Can be "low", "high", or "auto". Defaults to "auto".
            custom_prompt (str): Optional. A custom prompt to guide the analysis.
                                 If None, a default prompt is used.

        Returns:
            str: The analysis text from the OpenAI API.
                 Returns None if an error occurs.
        """
        if not isinstance(image_input_bytes, bytes):
            st.error("Invalid image input. Expected image bytes.")
            return None

        base64_image = self.encode_image(image_input_bytes)

        # Determine the content for the image
        image_content = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}", # Assume JPEG for base64
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


# --- 3. Intégration à l'application web Streamlit ---

st.set_page_config(page_title="OpenAI API Showcase", layout="wide") # Changed to wide layout for better spacing

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["DALL-E Image Generation", "ChatGPT Prompt Improvement", "OpenAI Vision Analysis"])

if page == "DALL-E Image Generation":
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

    # DALL-E Image Variation Section (Requires DALL-E 2 and local file upload)
    st.header("🔄 Create Image Variation (DALL-E 2)")
    st.info("This feature uses DALL-E 2 and requires you to upload an image. DALL-E 3 does not support direct image variations. Ensure the uploaded image is square (e.g., 512x512 or 1024x1024) and under 4MB.")

    uploaded_file_variation = st.file_uploader("Upload an image for variation (PNG or JPG recommended):", type=["png", "jpg", "jpeg"], key="variation_uploader")
    variation_prompt = st.text_input("Enter a prompt to guide the variation (optional):", "Make it look more ethereal.", key="variation_prompt_input")

    if st.button("Create Variation", key="create_variation_button"):
        if uploaded_file_variation is not None:
            # Save the uploaded file temporarily
            temp_file_path = "temp_image_for_variation.png"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file_variation.getbuffer())

            st.info("Creating image variation... This may take a moment.")
            with st.spinner('Varying...'):
                # DALL-E 2 generate_variation does not explicitly use the prompt in the same way DALL-E 3 does for generation.
                # The prompt here primarily serves as a description for the user about the desired change.
                variation_image_url = openai_create_image_variation(temp_file_path, variation_prompt)

                if variation_image_url:
                    st.success("Image variation created successfully!")
                    st.image(variation_image_url, caption="Image Variation", use_column_width=True)
                    st.write(f"[Download Variation]({variation_image_url})")
                else:
                    st.error("Failed to create image variation.")

            # Clean up the temporary file
            os.remove(temp_file_path)
        else:
            st.warning("Please upload an image to create a variation.")


elif page == "ChatGPT Prompt Improvement":
    st.title("✨ Improve Your Prompt with ChatGPT")
    st.markdown("Leverage ChatGPT to get more descriptive and creative prompts for image generation.")

    # ChatGPT Prompt Improvement Section
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

elif page == "OpenAI Vision Analysis":
    st.title("👁️ Image Analysis with OpenAI Vision")
    st.write("Upload an image and let OpenAI's `gpt-4o` model describe it for you.")

    # Initialize VisionProcessor using the globally initialized client
    vision_processor = VisionProcessor(client)

    uploaded_file_vision = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], key="vision_uploader")

    if uploaded_file_vision is not None:
        # Display the uploaded image
        st.image(uploaded_file_vision, caption='Uploaded Image.', use_column_width=True)
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

        if st.button("Analyze Image", key="analyze_image_button"):
            with st.spinner("Analyzing image... This may take a moment."):
                # Pass the raw bytes of the uploaded file
                analysis_result = vision_processor.vision_analyze_image(
                    uploaded_file_vision.read(),
                    detail=detail_option,
                    custom_prompt=custom_prompt_input
                )

            if analysis_result:
                st.subheader("Analysis Result:")
                st.markdown(f"**Description:**\n{analysis_result}")
            else:
                st.error("Could not get a valid analysis from the model.")

st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and OpenAI APIs.")

# --- Custom CSS for button styling ---
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
