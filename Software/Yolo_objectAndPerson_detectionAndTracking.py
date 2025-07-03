import cv2
from ultralytics import YOLO

model = YOLO('yolov9e.pt')  # plain detection model; adjust as needed

# Open laptop camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    results = model.track(frame, tracker='bytetrack.yaml', persist=True, conf=0.3, iou=0.5)
    annotated = results[0].plot()  # draw boxes + track IDs

    cv2.imshow('Keeping Eye', annotated)
    if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()
