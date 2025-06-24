import requests
import torch
import pyaudio
import wave
import pygame
import os
import tempfile
import numpy as np
import time

from fuzzywuzzy import fuzz

from TTS.api import TTS
from ws_server import start_websocket_server, send_log

from faster_whisper import WhisperModel

from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter


def print_log(message):
    print(message)
    send_log(message)

pygame.mixer.init()
device = "cuda" if torch.cuda.is_available() else "cpu"
print_log(f"Using device: {device}")

tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=torch.cuda.is_available())

default_language = "en"
default_speaker_wav = "Audio/sample-0.wav"
print_log(f"TTS model loaded. Using language: {default_language}")

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
            speed=0.01
        )
        # roboticize_audio(audio_path)
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
        return f"Sorry, I couldn't generate a response. Error is {e}"


def roboticize_audio(file_path):
    sound = AudioSegment.from_wav(file_path)

    # Step 1: Band-pass filter
    sound = low_pass_filter(sound, 4000)
    sound = high_pass_filter(sound, 300)

    # Step 2: Metallic echo
    echo = sound - 6
    sound = sound.overlay(echo, position=40)

    # Step 3: Tremolo
    duration_ms = len(sound)
    frame_ms = 100
    freq = 30
    mod_depth = 1

    modulated = AudioSegment.empty()
    sine_wave = np.sin(2 * np.pi * freq * np.arange(0, duration_ms, frame_ms) / 1000.0)

    for i, mod in zip(range(0, duration_ms, frame_ms), sine_wave):
        chunk = sound[i:i+frame_ms]
        volume_factor = 1 + mod_depth * mod
        chunk = chunk + (50 * (volume_factor - 1))
        modulated += chunk

    # Step 4: Bitcrushing
    modulated = modulated.set_frame_rate(11025)

    # Step 5: Vibrato simulation
    vibrato = AudioSegment.empty()
    vibrato_depth = 70
    vibrato_rate = 70

    for i in range(0, len(modulated), frame_ms):
        chunk = modulated[i:i+frame_ms]
        vibrato_offset = int(vibrato_depth * np.sin(2 * np.pi * vibrato_rate * i / 1000))
        vibrato_chunk = chunk
        if vibrato_offset > 0:
            vibrato_chunk = chunk.overlay(chunk, position=vibrato_offset)
        vibrato += vibrato_chunk

    # Save back to original file
    vibrato.export(file_path, format="wav")


def wait_for_wake_word(wake_words=["hey nuki", "hello nuki", "hi nuki" , "hey no key" , "hello no key" , "hey no key"], similarity_threshold=80):
    print_log("Listening for wake word...")

    RATE = 16000
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    LISTEN_DURATION = 2.5  # seconds

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    try:
        while True:
            frames = []
            for _ in range(0, int(RATE / CHUNK * LISTEN_DURATION)):
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
                path = tmpfile.name
            with wave.open(path, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            try:
                segments, _ = model.transcribe(path, language="en")
                spoken_text = " ".join([segment.text for segment in segments]).lower().strip()
                print_log(f"Wake word check heard: \"{spoken_text}\"")

                for wake_word in wake_words:
                    similarity = fuzz.partial_ratio(wake_word.lower(), spoken_text)
                    print_log(f"Checking similarity with \"{wake_word}\" → {similarity}%")

                    if similarity >= similarity_threshold:
                        print_log(f"Wake word '{wake_word}' detected with {similarity}% similarity.")
                        return

            except Exception as e:
                print_log(f"Wake word detection error: {e}")
            finally:
                if os.path.exists(path):
                    os.remove(path)

            time.sleep(0.2)  # Small delay before next listen

    except KeyboardInterrupt:
        print_log("Wake word listening interrupted by user.")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


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
                clean_response = response.replace("*", "")
                print_log(f"Assistant: {clean_response}")
                text_to_speech(clean_response)
            else:
                text_to_speech("I didn't catch that.")
        except KeyboardInterrupt:
            print_log("Exiting...")
            text_to_speech("Have a great Day!")
            break
        except Exception as e:
            print_log(f"Runtime error: {e}")
            text_to_speech(f"Sorry, I had an issue. Error is {e}")

if __name__ == "__main__":
    main_loop()


