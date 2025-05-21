# google speech recognition code

import speech_recognition as sr
import pygame

pygame.mixer.init()

def play_sound(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(5)

def listen_to_voice():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        play_sound("./listen.mp3")
        audio = recognizer.listen(source)

        play_sound("./convert.mp3")

        text = recognizer.recognize_google(audio)
        print("You said: " + text)
        return text
    


listen_to_voice();

