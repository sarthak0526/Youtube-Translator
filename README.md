
# LangBridge - AI-Powered YouTube Video Translation

LangBridge is a simple web application that allows users to translate YouTube videos from one language to another using AI-powered tools. 
The system supports a variety of languages, including regional languages, making educational content accessible to users worldwide.

## Features:
- **Real-time Language Translation:** Converts YouTube video transcripts into multiple languages.
- **Speech Recognition:** If no transcript is available, the system converts audio to text using speech recognition.
- **Text-to-Speech:** Translates the transcript and generates audio using Google Text-to-Speech (gTTS).
- **Video Synchronization:** Syncs the translated audio with the original video using MoviePy.
- **User-friendly Interface:** Provides a simple interface to input YouTube video links and select languages.

## How It Works:
1. The user inputs a YouTube video link and selects the source and target languages.
2. The system checks the video for available transcripts or uses speech recognition to transcribe the video.
3. The transcript is translated into the target language.
4. The translated text is converted into speech, and the new audio is synchronized with the video.
5. The user receives a translated version of the video with new audio.

## Requirements:
Make sure you have Python installed. You can install the necessary dependencies using `pip`.

To install dependencies, run:
```
pip install -r requirements.txt
```

## Usage:
1. Clone this repository:
   ```
   git clone https://github.com/yourusername/langbridge.git
   ```
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```

4. Open your browser and access the Gradio interface to translate YouTube videos.

## Supported Languages:
- Major Languages: English, Spanish, French, German, Chinese, Japanese, Russian, etc.
- Regional Languages: Hindi, Bengali, Telugu, Tamil, Kannada, Marathi, and more.

## Future Improvements:
- Supporting longer videos
- Adding more regional languages
- Integration with educational platforms

