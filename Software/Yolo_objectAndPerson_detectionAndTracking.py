import cv2
from ultralytics import YOLO

# Load the YOLO model
model = YOLO('yolov9e.pt')  # adjust model path as necessary

# Open IP camera stream
cap = cv2.VideoCapture("http://192.168.8.158:81/stream")

# Check if the stream is opened correctly
if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Run tracking
    results = model.track(frame, tracker='bytetrack.yaml', persist=True, conf=0.3, iou=0.5)
    annotated = results[0].plot()  # draw boxes and IDs

    # Display the result
    cv2.imshow('Keeping Eye', annotated)

    # Exit on pressing 'q'
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
