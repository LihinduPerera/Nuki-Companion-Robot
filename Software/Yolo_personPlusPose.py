import cv2
from ultralytics import YOLO

detect = YOLO('yolo11n.pt')       # person detector
pose = YOLO('yolo11n-pose.pt')    # pose model

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    det_res = detect.track(frame, tracker='bytetrack.yaml', persist=True, conf=0.3, iou=0.5)
    tracks = det_res[0]

    for det in tracks.boxes:
        cls = int(det.cls)
        if detect.names[cls] != 'person': continue
        x1, y1, x2, y2 = map(int, det.xyxy[0])

        crop = frame[y1:y2, x1:x2]
        p = pose.predict(crop, imgsz=256, device=0)[0]
        crop = p.plot()  # skeleton overlay
        frame[y1:y2, x1:x2] = crop

    cv2.imshow('Companion Vision', frame)
    if cv2.waitKey(1) == ord('q'): break

cap.release()
cv2.destroyAllWindows()
