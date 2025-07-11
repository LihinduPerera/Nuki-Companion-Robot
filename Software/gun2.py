import cv2 as cv
import time
import HandTrackingModule as htm
import numpy as np
import pygame
import torch
import tempfile
import os
import threading
import requests
from TTS.api import TTS

# Initialize pygame and TTS
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

def handle_gun_response(text):
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

        try:
            # Robot animation (optional)
            requests.get("http://192.168.8.101/A4", timeout=2)
            requests.get("http://192.168.8.101/M1?angle=90", timeout=2)
        except requests.RequestException as e:
            print(f"Robot command failed: {e}")

    except Exception as e:
        print(f"TTS or request failed: {e}")

def gun_action_async():
    threading.Thread(
        target=handle_gun_response,
        args=("Bang! Got you!",),
        daemon=True
    ).start()

class GunGestureDetector:
    def __init__(self):
        pass

def is_gun_gesture(self, lmList):
    if len(lmList) < 21:
        return False

    # Extract coordinates
    def get_xyz(index): return lmList[index][1], lmList[index][2], lmList[index][3]

    # Key landmarks
    wrist = get_xyz(0)
    index_tip = get_xyz(8)
    index_mcp = get_xyz(5)
    middle_tip = get_xyz(12)
    ring_tip = get_xyz(16)
    pinky_tip = get_xyz(20)
    thumb_tip = get_xyz(4)
    thumb_ip = get_xyz(3)

    # 1. Index finger pointing forward (Z difference)
    index_depth = wrist[2] - index_tip[2]
    index_forward = index_depth > 0.08  # Tune this threshold if needed

    # 2. Other fingers curled (tips behind wrist in Z)
    def is_curled(finger_tip): return finger_tip[2] > wrist[2] - 0.03

    curled_fingers = [
        is_curled(middle_tip),
        is_curled(ring_tip),
        is_curled(pinky_tip)
    ]
    curled_count = sum(curled_fingers)

    # 3. Thumb sideways or not forward (allowing some flexibility)
    thumb_sideways = abs(thumb_tip[0] - thumb_ip[0]) > abs(thumb_tip[2] - thumb_ip[2])

    # Final rule: index forward, thumb sideways, 2+ curled fingers
    return index_forward and curled_count >= 2 and thumb_sideways


def main():
    cap = cv.VideoCapture(0)
    detector = htm.handDetector(detectionCon=0.7, maxHands=1)
    gunDetector = GunGestureDetector()

    gesture_state = "NoGun"
    fire_cooldown = 2.5
    gun_shown_time = 0

    gun_detected_frames = 0
    gun_not_detected_frames = 0
    FRAMES_TO_CONFIRM = 5

    while True:
        success, img = cap.read()
        if not success:
            print("Camera error")
            continue

        img = cv.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False, returnZ=True)

        gun_detected = gunDetector.is_gun_gesture(lmList)
        current_time = time.time()

        if gun_detected:
            gun_detected_frames += 1
            gun_not_detected_frames = 0
        else:
            gun_detected_frames = 0
            gun_not_detected_frames += 1

        if gesture_state == "NoGun":
            if gun_detected_frames >= FRAMES_TO_CONFIRM:
                print("Gun Shown")
                gesture_state = "GunShown"
                gun_shown_time = current_time
        elif gesture_state == "GunShown":
            if gun_not_detected_frames >= FRAMES_TO_CONFIRM:
                print("Gun Removed")
                gesture_state = "NoGun"
            elif current_time - gun_shown_time >= fire_cooldown:
                print("Gun Fired")
                gun_action_async()
                gesture_state = "Cooldown"
                gun_shown_time = current_time
        elif gesture_state == "Cooldown":
            if gun_not_detected_frames >= FRAMES_TO_CONFIRM:
                gesture_state = "NoGun"

        # Visual debugging
        cv.putText(img, f'Gun Detected: {gun_detected}', (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0) if gun_detected else (0, 0, 255), 2)

        cv.imshow("Gun Gesture Detection", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
