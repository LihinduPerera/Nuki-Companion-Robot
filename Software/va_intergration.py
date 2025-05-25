# import whisper
# import torch
# import pyaudio
# import wave
# import pygame
# import pyttsx3
# import os
# import tempfile
# import google.generativeai as gemini
# from dotenv import load_dotenv

# load_dotenv()
# apiKey = os.getenv("API_KEY")
# print("API key loaded:", bool(apiKey))

# gemini.configure(api_key=apiKey)

# pygame.mixer.init()

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print("Using device:", device)

# def text_to_speech(text, voice_index=1, rate=170, volume=1.0):
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')

#     if voice_index >= len(voices):
#         voice_index = 0 

#     engine.setProperty('voice', voices[voice_index].id)
#     engine.setProperty('rate', rate)
#     engine.setProperty('volume', volume)

#     engine.say(text)
#     engine.runAndWait()

# try:
#     model = whisper.load_model("turbo", device=device)
#     print("Whisper model loaded successfully.")
# except Exception as e:
#     print("Failed to load Whisper model:", e)
#     text_to_speech("Failed to load the speech recognition model. Please check the configuration.")
#     exit(1)

# def play_sound(file_path):
#     pygame.mixer.music.load(file_path)
#     pygame.mixer.music.play()
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(10)

# def listen_to_voice():
#     RATE = 16000
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RECORD_SECONDS = 5

#     p = pyaudio.PyAudio()

#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#     text_to_speech("Listening...")

#     frames = []
#     for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#         data = stream.read(CHUNK)
#         frames.append(data)

#     stream.stop_stream()
#     stream.close()
#     p.terminate()

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
#         wf = wave.open(tmpfile.name, 'wb')
#         wf.setnchannels(CHANNELS)
#         wf.setsampwidth(p.get_sample_size(FORMAT))
#         wf.setframerate(RATE)
#         wf.writeframes(b''.join(frames))
#         wf.close()
#         audio_path = tmpfile.name


#     result = model.transcribe(audio_path)
#     print("You said:", result['text'])
#     return result['text']

# def llm_response(text):
#     gmodel = gemini.GenerativeModel(model_name="gemini-2.0-flash")
#     response = gmodel.generate_content(text)
#     print("Gemini:", response.text)
#     return response.text

# # Main loop
# while True:
#     try:
#         user_input = listen_to_voice()
#         response = llm_response(user_input)
#         text_to_speech(response)
#     except KeyboardInterrupt:
#         print("\nExiting...")
#         break
#     except Exception as e:
#         print("Error:", e)
#         text_to_speech("Sorry, I encountered an error.")

import whisper
import torch
import pyaudio
import wave
import pygame
import os
import tempfile
import google.generativeai as gemini
from dotenv import load_dotenv

from TTS.api import TTS

load_dotenv()
apiKey = os.getenv("API_KEY")
print("API key loaded:", bool(apiKey))

gemini.configure(api_key=apiKey)

pygame.mixer.init()

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

tts_model_name = "tts_models/en/vctk/vits"
tts = TTS(tts_model_name, progress_bar=False, gpu=torch.cuda.is_available())


default_speaker = tts.speakers[0] if tts.speakers else None
print(f"Using speaker: {default_speaker}")

def text_to_speech(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio_path = tmpfile.name

        tts.tts_to_file(text=text, speaker=default_speaker, file_path=audio_path)

        play_sound(audio_path)

    except Exception as e:
        print("TTS Error:", e)
    finally:

        try:
            pygame.mixer.music.stop()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.remove(audio_path)
        except Exception as cleanup_error:
            print("File deletion error:", cleanup_error)


def play_sound(file_path):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print("Audio Playback Error:", e)

try:
    model = whisper.load_model("base", device=device)
    print("Whisper model loaded successfully.")
except Exception as e:
    print("Failed to load Whisper model:", e)
    text_to_speech("Failed to load the speech recognition model. Please check the configuration.")
    exit(1)

def listen_to_voice():
    RATE = 16000
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    text_to_speech("Listening")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wf = wave.open(tmpfile.name, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        audio_path = tmpfile.name

    try:
        result = model.transcribe(audio_path)
        print("You said:", result['text'])
        return result['text']
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

def llm_response(text):
    try:
        gmodel = gemini.GenerativeModel(model_name="gemini-2.0-flash")
        response = gmodel.generate_content(text)
        print("Gemini:", response.text)
        return response.text
    except Exception as e:
        print("LLM Error:", e)
        return "Sorry, I couldn't generate a response."

# Main loop
if __name__ == "__main__":
    while True:
        try:
            user_input = listen_to_voice()
            if user_input.strip():
                response = llm_response(user_input)
                text_to_speech(response)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print("Runtime Error:", e)
            text_to_speech("Sorry, I encountered an error.")
