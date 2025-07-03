from ultralytics import YOLO
import cv2

pose_model = YOLO('yolo11n-pose.pt')  # YOLO11 nano pose model

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    results = pose_model.predict(frame, show=False, imgsz=640, device=0)
    frame = results[0].plot()  # draws skeleton + keypoints

    cv2.imshow('Pose', frame)
    if cv2.waitKey(1) == ord('q'): break
