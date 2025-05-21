# google speech recognition code

# import speech_recognition as sr
# import pygame

# pygame.mixer.init()

# def play_sound(file_path):
#     pygame.mixer.music.load(file_path)
#     pygame.mixer.music.play()
#     while pygame.mixer.music.get_busy():
#         pygame.time.Clock().tick(5)

# def listen_to_voice():
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("Listening...")
#         play_sound("./listen.mp3")
#         audio = recognizer.listen(source)

#         play_sound("./convert.mp3")

#         text = recognizer.recognize_google(audio)
#         print("You said: " + text)
#         return text
    


# listen_to_voice();

# Using VOSK --- (Offline)

import vosk
import pyaudio
import json
import pygame

pygame.mixer.init()
model = vosk.Model("E:/Projects/Robotics/Nuki -Companion Robot/PythonProject/py_logics/Ai_Models/vosk-model-en-us-0.22")
recognizer = vosk.KaldiRecognizer(model, 16000)

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(5)

def listen_to_voice():
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()
    print("Listening...")
    play_sound("E:/Projects/Robotics/Nuki -Companion Robot/PythonProject/py_logics/Audio/listen.mp3")

    while True:
        data = stream.read(8192)
        if len(data) == 0:
            continue

        if recognizer.AcceptWaveform(data):
            play_sound("E:/Projects/Robotics/Nuki -Companion Robot/PythonProject/py_logics/Audio/convert.mp3")
            result = recognizer.Result()
            text = json.loads(result)["text"]
            print("You said: " + text)
            return text
        


while True:
    listen_to_voice()