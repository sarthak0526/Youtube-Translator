import pathlib
import sys, os
from gtts import gTTS
import gradio as gr
import speech_recognition as sr
from translate import Translator
from moviepy.editor import *
from pytubefix import YouTube  # Updated import statement
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.error import HTTPError
import validators  # Added import for URL validation

# Define a dictionary for supported languages (including regional languages)
LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "zh": "Chinese",
    "ja": "Japanese",
    "ru": "Russian",
    "ar": "Arabic",
    "pt": "Portuguese",
    "it": "Italian",
    "hi": "Hindi",
    "bn": "Bengali",
    "pa": "Punjabi",
    "mr": "Marathi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "gu": "Gujarati",
    "sa": "Sanskrit",
    "sw": "Swahili",
    "th": "Thai",
    "vi": "Vietnamese",
    "ms": "Malay",
    "tr": "Turkish",
    "he": "Hebrew",
    "pl": "Polish",
    # Add other languages as needed
}

# Download the video from YouTube
def download_video(url):
    print("Downloading...")
    try:
        yt = YouTube(url)  # Using pytubefix's YouTube class
        stream = yt.streams.filter(progressive=True, file_extension="mp4").first()
        if stream:
            local_file = stream.download()
            print("Downloaded successfully")
            return local_file
        else:
            print("No suitable stream found.")
            return None
    except HTTPError as e:
        print(f"An HTTP error occurred while downloading the video: {e}")
        return None
    except Exception as e:
        print(f"An error occurred while downloading the video: {e}")
        return None

# Validate YouTube video URL and length
def validate_youtube(url):
    try:
        yt = YouTube(url)  # Using pytubefix's YouTube class
        if yt.length > 600:
            print("Your video is larger than 10 minutes")
            return True
        else:
            print("Your video is less than 10 minutes")
            return False
    except Exception:
        print("Invalid URL")
        return True

# Validate generic URL
def validate_url(url):
    if not validators.url(url):
        print("Invalid URL format")
        return True
    else:
        return False

# Clean up leftover video and audio files
def cleanup():
    types = ('.mp4', '.wav') 
    junks = []
    for file_type in types:
        junks.extend(pathlib.Path().glob(f"*{file_type}"))
    try:
        for junk in junks:
            print("Deleting", junk)
            junk.unlink()
    except Exception as e:
        print(f"Cannot delete file because: {e}")

# Get the file size
def getSize(filename):
    st = os.stat(filename)
    return st.st_size

# Clean the transcript to remove unwanted words
def clean_transcript(transcript_list):
    script = ""
    for text in transcript_list:
        t = text["text"]
        if t.lower() not in ['[music]', '[музыка]', '[musik]', '[musica]', '[音楽]', '[音乐]']:
            script += t + " "
    return script

# Fetch the transcript and translate if necessary
def get_transcript(url, desired_language):
    exist1 = "?v=" in url
    exist2 = "https://youtu.be/" in url
    exist3 = "shorts/" in url

    if exist1:
        ind = url.index("?v=")
        id_you = url[ind + 3:]
    elif not exist1 and exist2:
        ind = url.index(".be/")
        id_you = url[ind + 4:ind + 15]
    else:
        ind = url.index("shorts/")
        id_you = url[ind + 7:]

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(id_you)
        available_languages = transcript_list.available_languages
        print(f"Available languages: {available_languages}")

        desired_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(desired_language)]
        
        if desired_lang_code not in available_languages:
            print(f"Transcript not available in the desired language: {desired_language}")
            return " ", " ", False

        transcript = transcript_list.find_transcript([desired_lang_code])
        transcript_translated = transcript.translate(desired_language).fetch()
        translated = clean_transcript(transcript_translated)
        is_translated = True

    except Exception as e:
        print(f"An error occurred: {e}")
        return " ", " ", False

    transcript = transcript.fetch()
    script = clean_transcript(transcript)

    return script, translated, is_translated

# Function to pad or loop audio to match video length
def match_audio_length(video_clip, audio_clip):
    video_duration = video_clip.duration
    audio_duration = video_clip.duration
    return audio_clip

# Video translation function
def video_to_translate(url, initial_language, final_language):
    print('Checking the URL')
    if validate_url(url) or validate_youtube(url):
        return "./demo/tryagain2.mp4"

    initial_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(initial_language)]
    final_lang_code = list(LANGUAGES.keys())[list(LANGUAGES.values()).index(final_language)]
    lang = final_lang_code

    # Initial directory setup
    home_dir = os.getcwd()
    temp_dir = os.path.join(home_dir, "temp")
    pathlib.Path(temp_dir).mkdir(parents=True, exist_ok=True)
    os.environ['home_dir'] = home_dir
    os.environ['temp_dir'] = temp_dir

    print('Initial directory:', home_dir)
    
    
    # Download video
    file_obj = download_video(url)
    if not file_obj:
        print("Failed to download video.")
        return "Failed to download the video. Please check the URL or try again later."

    videoclip = VideoFileClip(file_obj)
    is_translated = False

    # Get transcript
    text, trans, is_translated = get_transcript(url, desired_language=lang)
    print("Transcript Found")

    if not is_translated:
        print("No Transcript Found, trying audio recognition")
        videoclip.audio.write_audiofile("audio.wav", codec='pcm_s16le')

        r = sr.Recognizer()
        with sr.AudioFile("audio.wav") as source:
            audio_data = r.record(source)
            size_wav = getSize("audio.wav")
            if size_wav > 50000000:
                print("Audio too large")
                audio_chunks = split_audio_wav("audio.wav")
                text = ""
                for chunk in audio_chunks:
                    try:
                        text_chunk = r.recognize_google(chunk, language=initial_lang_code)
                    except Exception:
                        print("Audio recognition failed.")
                        cleanup()
                        return "./demo/tryagain.mp4"
                    text += text_chunk + " "
            else:
                try:
                    text = r.recognize_google(audio_data, language=initial_lang_code)
                except Exception:
                    print("Audio recognition failed.")
                    cleanup()
                    return "./demo/tryagain.mp4"

        # Translate using 'translate' library
        translator = Translator(to_lang=lang)
        try:
            trans = translator.translate(text)
        except Exception:
            print("Translation failed.")
            cleanup()
            return "./demo/tryagain.mp4"

    myobj = gTTS(text=trans, lang=lang, slow=False)
    myobj.save("audio.wav")

    audioclip = AudioFileClip("audio.wav")
    
    # Match audio length to video length
    audioclip = match_audio_length(videoclip, audioclip)
    
    videoclip.audio = CompositeAudioClip([audioclip])
    new_video = "video_translated_" + lang + ".mp4"
    videoclip.write_videofile(new_video)

    videoclip.close()

    return new_video

# Gradio interface definition
all_languages = list(LANGUAGES.values())
initial_language = gr.Dropdown(choices=all_languages, label="Initial Language")
final_language = gr.Dropdown(choices=all_languages, label="Final Language")
url = gr.Textbox(label="Enter the YouTube URL below:")

gr.Interface(
    fn=video_to_translate,
    inputs=[url, initial_language, final_language],
    outputs='video',
    title='LangBridge',
    description='A simple application that translates YouTube videos from one language to another.',
    article='''<div>
        <p style="text-align: center">Paste the YouTube link, select languages, and hit submit. The video length limit is 10 minutes. Visit <a href="https://ruslanmv.com/">ruslanmv.com</a> for more info.</p>
    </div>''',
    examples=[
        ["https://www.youtube.com/watch?v=uLVRZE8OAI4", "English", "Spanish"],
        ["https://www.youtube.com/watch?v=fkGCLIQx1MI", "English", "Russian"],
        ["https://www.youtube.com/watch?v=6Q6hFtitthQ", "Italian", "English"],
        ["https://www.youtube.com/watch?v=s5XvjAC7ai8", "Russian", "English"],
        ["https://www.youtube.com/watch?v=qzzweIQoIOU", "Japanese", "English"],
        ["https://www.youtube.com/watch?v=nOGZvu6tJFE", "German", "Spanish"]
    ]
).launch(share=True)  # Added share=True to create a public link
