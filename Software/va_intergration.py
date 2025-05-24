import whisper
import torch
import pyaudio
import wave
import pygame
import pyttsx3
import os
import tempfile
import google.generativeai as gemini
from dotenv import load_dotenv

load_dotenv()
apiKey = os.getenv("API_KEY")
print("API key loaded:", bool(apiKey))

gemini.configure(api_key=apiKey)

pygame.mixer.init()

device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

def text_to_speech(text, voice_index=1, rate=170, volume=1.0):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if voice_index >= len(voices):
        voice_index = 0 

    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)

    engine.say(text)
    engine.runAndWait()

try:
    model = whisper.load_model("turbo", device=device)
    print("Whisper model loaded successfully.")
except Exception as e:
    print("Failed to load Whisper model:", e)
    text_to_speech("Failed to load the speech recognition model. Please check the configuration.")
    exit(1)

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def listen_to_voice():
    RATE = 16000
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    text_to_speech("Listening...")

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


    result = model.transcribe(audio_path)
    print("You said:", result['text'])
    return result['text']

def llm_response(text):
    gmodel = gemini.GenerativeModel(model_name="gemini-2.0-flash")
    response = gmodel.generate_content(text)
    print("Gemini:", response.text)
    return response.text

# Main loop
while True:
    try:
        user_input = listen_to_voice()
        response = llm_response(user_input)
        text_to_speech(response)
    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print("Error:", e)
        text_to_speech("Sorry, I encountered an error.")
