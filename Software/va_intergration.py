import vosk
import pyaudio
import pygame
import pyttsx3
import json
import google.generativeai as gemini
import os
from dotenv import load_dotenv

load_dotenv()
apiKey = os.getenv("API_KEY")
print(apiKey)

gemini.configure(api_key=apiKey)
pygame.mixer.init()
model = vosk.Model("E:/Projects/Robotics/Nuki -Companion Robot/PythonProject/py_logics/Ai_Models/vosk-model-en-us-0.22")
recognizer = vosk.KaldiRecognizer(model, 16000)

def text_to_speech(text, voice_index=1, rate=170, volume=1.0):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', rate)
    engine.setProperty('volume', volume)

    engine.say(text)
    engine.runAndWait()

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def listen_to_voice():
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.stop_stream()
    text_to_speech("Listening")
    stream.start_stream()

    while True:
        data = stream.read(8192)
        if len(data) == 0:
            continue

        if recognizer.AcceptWaveform(data):
            play_sound("E:/Projects/Robotics/Nuki -Companion Robot/PythonProject/py_logics/Audio/convert.mp3")
            result = recognizer.Result()
            text = json.loads(result)["text"]
            print("You said: "+text)
            return text

def llm_response(text):
    model = gemini.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(text)
    print(response.text)
    return response.text



while True:
    text = listen_to_voice()
    llm_output = llm_response(text)
    text_to_speech(llm_output)