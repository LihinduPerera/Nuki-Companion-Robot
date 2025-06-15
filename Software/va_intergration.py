import requests
import torch
import pyaudio
import wave
import pygame
import os
import tempfile

from TTS.api import TTS
from ws_server import start_websocket_server, send_log

from faster_whisper import WhisperModel

def print_log(message):
    print(message)
    send_log(message)

pygame.mixer.init()
device = "cuda" if torch.cuda.is_available() else "cpu"
print_log(f"Using device: {device}")

tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=torch.cuda.is_available())

default_language = "en"
default_speaker_wav = "Audio/sample-0.wav"
print_log(f"XTTS model loaded. Using language: {default_language}")

whisper_model_type = 'turbo'
try:
    model = WhisperModel(whisper_model_type, device=device, compute_type="float16" if device == "cuda" else "int8")
    print_log("FastWhisper model loaded successfully.")
except Exception as e:
    print_log(f"Failed to load FastWhisper model: {e}")
    exit(1)

def play_sound(file_path, should_delete=True):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Block the main thread until audio finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print_log(f"Audio Playback Error: {e}")
    finally:
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass
        if should_delete and os.path.exists(file_path):
            os.remove(file_path)

def text_to_speech(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio_path = tmpfile.name
        tts.tts_to_file(
            text=text,
            file_path=audio_path,
            speaker=tts.speakers[34],  # 3 ,24 , 17 , 18(cute) , 33 , 34(Ep and voice is good)
            # 37(good ep voice) , 44(cute) , 45 , 47 , 48 , 49 , 51 , 54 , 58(robot like)
            #  64 , 65 , 67 , 75(cute)
            speed=0.09
        )
        play_sound(audio_path)
    except Exception as e:
        print_log(f"TTS Error: {e}")

def record_audio(duration=5):
    RATE = 16000
    CHUNK = 1024
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
        segments, info = model.transcribe(path,language="en")
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    except Exception as e:
        print_log(f"Transcription Error: {e}")
        return ""
    finally:
        if os.path.exists(path):
            os.remove(path)

# Global history list
conversation_history = []

def llm_response(prompt):
    try:
        # Append user input to history
        conversation_history.append(f"User: {prompt}")

        # Join all history for context
        full_prompt = "\n".join(conversation_history) + "\nAssistant:"

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2",
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        reply = response.json().get("response", "").strip()

        # Append assistant reply to history
        conversation_history.append(f"Assistant: {reply}")

        return reply
    except Exception as e:
        print_log(f"LLM Error: {e}")
        return "Sorry, I couldn't generate a response."


def wait_for_wake_word():
    wake_words = ["hey", "hello", "noki", "nuki"]
    wake_words = [w.lower() for w in wake_words]

    print_log(f"Waiting for wake words: {wake_words} ...")
    while True:
        path = record_audio(duration=5)
        text = transcribe_audio(path).lower()
        print_log(f"Heard (wake): {text}")
        if any(wake_word in text for wake_word in wake_words):
            return

def main_loop():
    start_websocket_server()
    
    while True:
        try:
            # text_to_speech("Hellow I'm nuki, I'm new TTS model for Text to speech. Testing 1, Testing 2 , Testing 3 , Testing Testing")
            wait_for_wake_word()
            # text_to_speech("Yes? How can I help you!")
            play_sound('Audio/deep2.mp3', should_delete=False)
            audio_path = record_audio(duration=5)
            user_text = transcribe_audio(audio_path)
            print_log(f"You said: {user_text}")

            if user_text:
                response = llm_response(user_text)
                print_log(f"Assistant: {response}")
                text_to_speech(response)
            else:
                text_to_speech("I didn't catch that.")
        except KeyboardInterrupt:
            print_log("Exiting...")
            text_to_speech("Have a great Day!")
            break
        except Exception as e:
            print_log(f"Runtime error: {e}")
            text_to_speech("Sorry, I had an issue.")

if __name__ == "__main__":
    main_loop()