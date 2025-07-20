# recognize_gesture.py
import cv2
import mediapipe as mp
import numpy as np
import joblib

# Load model and labels
model = joblib.load("gesture_model.pkl")
labels = np.load("labels.npy")

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=2,
                       min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

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

        if len(landmarks_all) > 0:
            try:
                prediction = model.predict([landmarks_all])[0]
                gesture_name = labels[prediction]
                cv2.putText(image, f"Gesture: {gesture_name}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 0), 3)
            except:
                pass

        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Gesture Recognition", image)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
