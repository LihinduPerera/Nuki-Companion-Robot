# collect_data.py
import cv2
import mediapipe as mp
import numpy as np
import os

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

gesture_name = input("heart")
save_path = f"data/{gesture_name}"
os.makedirs(save_path, exist_ok=True)

stream_url = 'http://192.168.8.158:81/stream'
cap = cv2.VideoCapture(0)
counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        landmarks_all = []
        for hand_landmarks in result.multi_hand_landmarks:
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            landmarks_all.extend(landmarks)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            np.save(f"{save_path}/{counter}.npy", np.array(landmarks_all))
            print(f"Saved {gesture_name} - sample {counter}")
            counter += 1

        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.putText(image, f"Press 's' to save {gesture_name}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Collecting Data", image)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()