import cv2 as cv
import time
import HandTrackingModule as htm

import torch
import tempfile
import pygame
import os
import requests
import threading
import numpy as np

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

def handle_wave_response(text):
    # TTS + Robot Animation Combined Async Function
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
            audio_path = tmpfile.name

        tts.tts_to_file(
            text=text,
            file_path=audio_path,
            speaker=tts.speakers[34],
            speed=0.1
        )

        play_sound(audio_path)

        try:
            requests.get("http://192.168.8.101/A6", timeout=2)
            requests.get("http://192.168.8.101/M1?angle=180", timeout=2)
        except requests.RequestException as e:
            print(f"Failed to trigger robot animation: {e}")

    except Exception as e:
        print(f"TTS or Request Error: {e}")

def wave_action_async():
    threading.Thread(
        target=handle_wave_response,
        args=("Hello! I see you waving! How are you today?",),
        daemon=True
    ).start()

class WaveDetector:
    def __init__(self, min_amplitude=80, min_waves=2, cooldown=2.0, wave_timeout=1.5):
        self.min_amplitude = min_amplitude
        self.min_waves = min_waves
        self.cooldown = cooldown
        self.wave_timeout = wave_timeout

        self.positions = []  # list of (timestamp, x_position)
        self.last_detection_time = 0
        self.wave_peaks = []
        self.last_peak_time = 0

    def update(self, x):
        now = time.time()

        if now - self.last_detection_time < self.cooldown:
            return False

        self.positions.append((now, x))
        self.positions = [(t, px) for t, px in self.positions if now - t < 1.5]

        if len(self.positions) < 5:
            return False

        xs = np.array([pos[1] for pos in self.positions])
        smoothed_xs = np.convolve(xs, np.ones(5)/5, mode='valid')

        peaks = []
        for i in range(1, len(smoothed_xs)-1):
            if smoothed_xs[i-1] < smoothed_xs[i] > smoothed_xs[i+1]:
                peaks.append(('max', smoothed_xs[i], self.positions[i+2][0]))
            elif smoothed_xs[i-1] > smoothed_xs[i] < smoothed_xs[i+1]:
                peaks.append(('min', smoothed_xs[i], self.positions[i+2][0]))

        self.wave_peaks = [p for p in peaks if now - p[2] < self.wave_timeout]

        wave_count = 0
        for i in range(1, len(self.wave_peaks)):
            prev, curr = self.wave_peaks[i-1], self.wave_peaks[i]
            if prev[0] != curr[0]:
                amplitude = abs(curr[1] - prev[1])
                if amplitude > self.min_amplitude:
                    wave_count += 1

        if wave_count >= self.min_waves:
            self.wave_peaks.clear()
            self.last_detection_time = now
            print(f"Wave Detected! Count: {wave_count}")
            return True
        return False

def main():
    cap = cv.VideoCapture(0)

    detector = htm.handDetector()
    waveDetector = WaveDetector(min_amplitude=80, min_waves=3, cooldown=2.0, wave_timeout=3.0)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from stream.")
            continue

        img = cv.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=True)

        if lmList:
            index_finger_x = lmList[8][1]
            if waveDetector.update(index_finger_x):
                print("Wave detected!")
                wave_action_async()

        cv.imshow("ESP32-CAM Stream", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
