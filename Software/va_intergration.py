# import whisper
# import torch
# import pyaudio
# import wave
# import pygame
# import os
# import tempfile
# import google.generativeai as gemini
# from dotenv import load_dotenv

# from TTS.api import TTS

# load_dotenv()
# apiKey = os.getenv("API_KEY")
# print("API key loaded:", bool(apiKey))

# gemini.configure(api_key=apiKey)

# pygame.mixer.init()

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print("Using device:", device)

# tts_model_name = "tts_models/en/vctk/vits"
# tts = TTS(tts_model_name, progress_bar=False, gpu=torch.cuda.is_available())


# default_speaker = tts.speakers[0] if tts.speakers else None
# print(f"Using speaker: {default_speaker}")

# def text_to_speech(text):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
#             audio_path = tmpfile.name

#         tts.tts_to_file(
#             text=text,
#             speaker=default_speaker,
#             file_path=audio_path,
#             length_scale=2)

#         play_sound(audio_path)

#     except Exception as e:
#         print("TTS Error:", e)
#     finally:

#         try:
#             pygame.mixer.music.stop()
#             while pygame.mixer.music.get_busy():
#                 pygame.time.Clock().tick(10)
#             os.remove(audio_path)
#         except Exception as cleanup_error:
#             print("File deletion error:", cleanup_error)


# def play_sound(file_path):
#     try:
#         pygame.mixer.music.load(file_path)
#         pygame.mixer.music.play()
#         while pygame.mixer.music.get_busy():
#             pygame.time.Clock().tick(10)
#     except Exception as e:
#         print("Audio Playback Error:", e)

# try:
#     model = whisper.load_model("turbo", device=device)
#     print("Whisper model loaded successfully.")
# except Exception as e:
#     print("Failed to load Whisper model:", e)
#     text_to_speech("Failed to load the speech recognition model. Please check the configuration.")
#     exit(1)

# def listen_to_voice():
#     RATE = 16000
#     CHUNK = 1024
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RECORD_SECONDS = 5

#     p = pyaudio.PyAudio()
#     stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#     text_to_speech("Listening")

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

#     try:
#         result = model.transcribe(audio_path)
#         print("You said:", result['text'])
#         return result['text']
#     finally:
#         if os.path.exists(audio_path):
#             os.remove(audio_path)

# def llm_response(text):
#     try:
#         gmodel = gemini.GenerativeModel(model_name="gemini-2.0-flash")
#         response = gmodel.generate_content(text)
#         print("Gemini:", response.text)
#         return response.text
#     except Exception as e:
#         print("LLM Error:", e)
#         return "Sorry, I couldn't generate a response."

# # Main loop
# if __name__ == "__main__":
#     while True:
#         try:
#             user_input = listen_to_voice()
#             if user_input.strip():
#                 response = llm_response(user_input)
#                 text_to_speech(response)
#         except KeyboardInterrupt:
#             print("\nExiting...")
#             text_to_speech("Exiting")
#             break
#         except Exception as e:
#             print("Runtime Error:", e)
#             text_to_speech("Sorry, I encountered an error.")

import whisper
import torch
import pyaudio
import wave
import pygame
import os
import tempfile
import threading
from dotenv import load_dotenv
from TTS.api import TTS
import google.generativeai as gemini

load_dotenv()
apiKey = os.getenv("API_KEY")
gemini.configure(api_key=apiKey)

pygame.mixer.init()
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Using device:", device)

tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=torch.cuda.is_available())
default_speaker = tts.speakers[0] if tts.speakers else None
print(f"Using speaker: {default_speaker}")

try:
    model = whisper.load_model("turbo", device=device)
    print("Whisper model loaded successfully.")
except Exception as e:
    print("Failed to load Whisper model:", e)
    exit(1)

def play_sound(file_path):
    def _play():
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        except Exception as e:
            print("Audio Playback Error:", e)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    threading.Thread(target=_play).start()

def text_to_speech(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio_path = tmpfile.name
        tts.tts_to_file(text=text, speaker=default_speaker, file_path=audio_path, length_scale=1.5)
        play_sound(audio_path)
    except Exception as e:
        print("TTS Error:", e)

def record_audio(duration=5):
    RATE = 16000
    CHUNK = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        path = tmpfile.name
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    return path

def transcribe_audio(path):
    try:
        result = model.transcribe(path, language="en", task="transcribe")
        return result["text"].strip()
    except Exception as e:
        print("Transcription Error:", e)
        return ""
    finally:
        if os.path.exists(path):
            os.remove(path)

def llm_response(prompt):
    try:
        gmodel = gemini.GenerativeModel(model_name="gemini-2.0-flash")
        response = gmodel.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("LLM Error:", e)
        return "Sorry, I couldn't generate a response."

def wait_for_wake_word():
    wake_words = ["hey", "hello", "noki", "nuki"]
    wake_words = [w.lower() for w in wake_words]

    print(f"Waiting for wake words: {wake_words} ...")
    while True:
        path = record_audio(duration=5)
        text = transcribe_audio(path).lower()
        print(f"Heard (wake): {text}")
        if any(wake_word in text for wake_word in wake_words):
            return

def main_loop():
    while True:
        try:
            wait_for_wake_word()
            text_to_speech("Yes? How can I help you!")
            audio_path = record_audio(duration=5)
            user_text = transcribe_audio(audio_path)
            print(f"You said: {user_text}")

            if user_text:
                response = llm_response(user_text)
                print(f"Assistant: {response}")
                text_to_speech(response)
            else:
                text_to_speech("I didn't catch that.")
        except KeyboardInterrupt:
            print("Exiting...")
            text_to_speech("Have a great Day!")
            break
        except Exception as e:
            print("Runtime error:", e)
            text_to_speech("Sorry, I had an issue.")

if __name__ == "__main__":
    main_loop()
