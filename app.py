import streamlit as st
import streamlit.components.v1 as components
import os
import tempfile
from moviepy.editor import VideoFileClip
from openai import OpenAI
from dotenv import load_dotenv
import time
import re
import mimetypes
import base64

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up session state for rate limiting and storing results
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'translations' not in st.session_state:
    st.session_state.translations = {}
if 'show_app' not in st.session_state:
    st.session_state.show_app = False

# Function to load and encode images
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Function to set background image
def set_background(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# CSS for animations
def local_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def is_valid_video_file(file):
    allowed_mime_types = ['video/mp4', 'video/avi', 'video/quicktime']
    file_type, _ = mimetypes.guess_type(file.name)
    return file_type in allowed_mime_types

def sanitize_input(input_string):
    return re.sub(r'[^a-zA-Z\s]', '', input_string)

def rate_limit():
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 60:  # 1 minute cooldown
        st.error("Please wait before making another request.")
        return False
    st.session_state.last_request_time = current_time
    return True

def convert_video_to_audio(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        temp_video_path = temp_video.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        try:
            with VideoFileClip(temp_video_path) as video:
                video.audio.write_audiofile(temp_audio.name)
                duration = video.duration
            return temp_audio.name, duration
        except Exception as e:
            st.error(f"Error processing video: {str(e)}")
            return None, 0
        finally:
            os.unlink(temp_video_path)

def transcribe_audio(audio_file):
    try:
        with open(audio_file, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio
            )
        return transcript.text
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def translate_text(text, target_language):
    try:
        sanitized_language = sanitize_input(target_language)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a translator. Translate the following text to {sanitized_language}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error translating text: {str(e)}")
        return None

def show_landing_page():
    st.markdown("""
    <div class="landing-container">
        <h1 class="main-title">TranscribeAI</h1>
        <p class="subtitle">Transcribe and translate your videos with AI technology.</p>
    </div>
    """, unsafe_allow_html=True)
    
    components.html("""
        <div class="video-container">
            <iframe width="560" height="315" src="https://www.youtube.com/embed/J65XkTx744M" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
        </div>
    """, height=350)
       
    st.markdown("""
    <div class="landing-container">
        <h2 class="section-title">Features</h2>
        <div class="features-container">
            <div class="feature-card">
                <h3>AI-Powered Transcription</h3>
                <p>Accurate transcription using OpenAI's Whisper model</p>
            </div>
            <div class="feature-card">
                <h3>Multi-Language Translation</h3>
                <p>Translate your content into multiple languages</p>
            </div>
            <div class="feature-card">
                <h3>Secure File Handling</h3>
                <p>Secure file upload and processing</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Get Started", key="get_started"):
        st.session_state.show_app = True

def main():
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key is not set. Please check your .env file.")
        return

    # Set background image
    set_background('background.png')  # Make sure to have a background.png file in your project directory

    # Load custom CSS
    local_css("style.css")  # Make sure to create a style.css file with the provided CSS

    show_landing_page()

    if st.session_state.show_app:
        st.title("AI-Supported Video Processor")
        
        # Language selection
        languages = ["Turkish", "English", "Russian", "French", "Spanish", "German", "Italian", "Japanese", "Chinese"]
        selected_languages = st.multiselect("Select target languages for translation:", languages)

        # Video file upload
        uploaded_file = st.file_uploader("Choose a video file (max 200MB)", type=["mp4", "avi", "mov"])

        if uploaded_file is not None:
            # Check file size and type
            if uploaded_file.size > 200 * 1024 * 1024:
                st.error("File size exceeds 200MB limit. Please upload a smaller file.")
            elif not is_valid_video_file(uploaded_file):
                st.error("Invalid file type. Please upload a valid video file.")
            else:
                st.video(uploaded_file)

                if st.button("Process Video") and rate_limit():
                    with st.spinner("Processing video..."):
                        # Convert video to audio
                        audio_file, duration = convert_video_to_audio(uploaded_file)
                        if audio_file:
                            # Transcribe audio
                            st.session_state.transcript = transcribe_audio(audio_file)
                            if st.session_state.transcript:
                                st.session_state.translations = {}
                                for lang in selected_languages:
                                    translation = translate_text(st.session_state.transcript, lang)
                                    if translation:
                                        st.session_state.translations[lang] = translation

                            # Clean up temporary audio file
                            os.unlink(audio_file)

        # Display results (outside of the file upload block to persist)
        if st.session_state.transcript:
            st.subheader("Original Transcript")
            st.write(st.session_state.transcript)

            # Provide download option for transcript
            st.download_button(
                label="Download Transcript",
                data=st.session_state.transcript,
                file_name="transcript.txt",
                mime="text/plain"
            )

            # Display translations
            for lang, translation in st.session_state.translations.items():
                st.subheader(f"{lang} Translation")
                st.write(translation)

                # Provide download option
                st.download_button(
                    label=f"Download {lang} Translation",
                    data=translation,
                    file_name=f"{sanitize_input(lang.lower())}_translation.txt",
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()