# AI Video Transcriber

AI Video Transcriber is a Streamlit-based web application that allows users to upload video files, transcribe the audio content, and translate the transcription into multiple languages using AI technology.

## Features

- Video upload (supports MP4, AVI, and MOV formats)
- AI-powered audio transcription using OpenAI's Whisper model
- Multi-language translation of transcripts
- Secure file handling
- Downloadable transcripts and translations

## Requirements

- Python 3.7+
- OpenAI API key
- Streamlit
- MoviePy
- OpenAI Python library
- python-dotenv

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/zsevall/Upschool-AI.git
   cd Upschool-AI
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

2. Open your web browser and go to the provided local URL (usually `http://localhost:8501`).

3. Upload a video file (max 200MB) and select target languages for translation.

4. Click "Process Video" to start the transcription and translation process.

5. View and download the generated transcript and translations.

## Note

This application uses OpenAI's API, which may incur costs. Please be aware of your API usage and any associated fees.

## License

[MIT License](LICENSE)
