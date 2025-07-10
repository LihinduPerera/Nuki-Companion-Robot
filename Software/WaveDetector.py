import cv2 as cv
import time
import HandTrackingModule as htm

import torch
import tempfile
import pygame
import os
import requests
import threading

from TTS.api import TTS

# Initialize Pygame and TTS
pygame.mixer.init()
tts = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=torch.cuda.is_available())

def play_sound(file_path, should_delete=True):
    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Audio Playback Error: {e}")
    finally:
        try:
            pygame.mixer.music.unload()
        except Exception:
            pass
        if should_delete and os.path.exists(file_path):
            os.remove(file_path)

def tts_thread_function(text):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio_path = tmpfile.name
        tts.tts_to_file(
            text=text,
            file_path=audio_path,
            speaker=tts.speakers[34],
            speed=1.0
        )
        play_sound(audio_path)
    except Exception as e:
        print(f"TTS Error: {e}")

def text_to_speech_async(text):
    threading.Thread(target=tts_thread_function, args=(text,), daemon=True).start()

class WaveDetector:
    def __init__(self, min_amplitude=50, min_waves=3, cooldown=2.0, wave_timeout=3.0):
        """
        min_amplitude: minimum horizontal movement in pixels to consider a wave
        min_waves: number of back-and-forth waves required
        cooldown: seconds to wait after detection before detecting again
        wave_timeout: max seconds allowed between waves before resetting count
        """
        self.min_amplitude = min_amplitude
        self.min_waves = min_waves
        self.cooldown = cooldown
        self.wave_timeout = wave_timeout
        
        self.positions = []
        self.last_wave_time = 0
        self.wave_count = 0
        self.last_direction = 0  # +1 or -1 for direction of movement
        self.last_detection_time = 0

    def update(self, x):
        """
        Call this every frame with the current wrist x position.
        Tracks direction changes and counts waves.
        """
        now = time.time()

        # If cooldown active, ignore updates
        if now - self.last_detection_time < self.cooldown:
            return
        
        # Remove old positions to keep window manageable (last 2 seconds)
        self.positions.append((now, x))
        self.positions = [(t, pos) for (t, pos) in self.positions if now - t < 2]

        # If we don't have enough points yet, wait
        if len(self.positions) < 5:
            return
        
        # Calculate movement direction based on last two points
        prev_x = self.positions[-2][1]
        dx = x - prev_x

        # If movement is too small, ignore
        if abs(dx) < 5:
            return
        
        current_direction = 1 if dx > 0 else -1
        
        # Check for direction change
        if self.last_direction != 0 and current_direction != self.last_direction:
            # Calculate amplitude of wave
            # Find min and max x in last positions to estimate amplitude
            xs = [pos for _, pos in self.positions]
            amplitude = max(xs) - min(xs)

            # Only count if amplitude is big enough
            if amplitude >= self.min_amplitude:
                # Check if waves are happening within wave_timeout
                if now - self.last_wave_time > self.wave_timeout:
                    # Too much time passed, reset wave count
                    self.wave_count = 0

                self.wave_count += 1
                self.last_wave_time = now

                # Debug print for wave count and amplitude
                print(f"Wave movement detected! Count: {self.wave_count}, Amplitude: {amplitude}")

        self.last_direction = current_direction

    def detect_wave(self):
        """
        Returns True if enough waves detected and resets counter + cooldown.
        """
        now = time.time()
        if self.wave_count >= self.min_waves:
            # Reset wave count and start cooldown
            self.wave_count = 0
            self.last_detection_time = now
            return True
        return False

def main():
    stream_url = 'http://192.168.8.158:81/stream'  # Change as needed
    cap = cv.VideoCapture(stream_url)

    detector = htm.handDetector()
    waveDetector = WaveDetector(min_amplitude=50, min_waves=3, cooldown=2.0, wave_timeout=3.0)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from stream.")
            continue

        img = cv.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=True)

        if lmList:
            wrist_x = lmList[0][1]  # Wrist x-coordinate
            waveDetector.update(wrist_x)

            if waveDetector.detect_wave():
                print("Wave detected!")
                text_to_speech_async("Hello! I see you waving! How are you today?")
                try:
                    requests.get("http://192.168.8.101/A6")
                    requests.get("http://192.168.8.101/M1?angle=180")
                except requests.RequestException as e:
                    print(f"Failed to trigger robot animation: {e}")

        cv.imshow("ESP32-CAM Stream", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
