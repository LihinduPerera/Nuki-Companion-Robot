import cv2
import mediapipe as mp
import csv

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Define the gesture label you're collecting (change each run)
gesture_label = "hi"

# Open CSV file to save landmarks
with open('gesture_data.csv', 'a', newline='') as f:
    csv_writer = csv.writer(f)
    
    stream_url = 'http://192.168.8.158:81/stream'
    cap = cv2.VideoCapture(stream_url)
    print(f"Collecting data for gesture: {gesture_label}")
    count = 0

    while count < 200:  # collect 200 frames
        success, img = cap.read()
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for handLms in result.multi_hand_landmarks:
                lm = []
                for id, lm_data in enumerate(handLms.landmark):
                    lm.extend([lm_data.x, lm_data.y, lm_data.z])
                lm.append(gesture_label)
                csv_writer.writerow(lm)
                count += 1
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Collecting", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()