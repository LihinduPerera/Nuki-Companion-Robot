import cv2 as cv
import time
import numpy as np
import HandTrackingModule as htm  # Your provided hand detector

import math

class HeartGestureDetector:
    def __init__(self, thumb_threshold=40, index_threshold=40, angle_threshold=30, cooldown=2.5):
        self.thumb_threshold = thumb_threshold
        self.index_threshold = index_threshold
        self.angle_threshold = angle_threshold  # max angle difference in degrees
        self.cooldown = cooldown
        self.last_detection_time = 0

    def _distance(self, p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def _angle_between_points(self, p1, p2):
        # Calculate angle in degrees between two points relative to horizontal
        delta = np.array(p2) - np.array(p1)
        angle = math.degrees(math.atan2(delta[1], delta[0]))
        return angle

    def is_heart(self, lmList1, lmList2):
        now = time.time()
        if now - self.last_detection_time < self.cooldown:
            return False

        # Extract key points
        thumb1 = lmList1[4][1:3]
        index1 = lmList1[8][1:3]
        middle1 = lmList1[12][1:3]

        thumb2 = lmList2[4][1:3]
        index2 = lmList2[8][1:3]
        middle2 = lmList2[12][1:3]

        # Distances between thumb tips and index fingertips
        dist_thumb = self._distance(thumb1, thumb2)
        dist_index = self._distance(index1, index2)

        # Angle between thumb tips and index fingertips for both hands
        angle_thumb = self._angle_between_points(thumb1, thumb2)
        angle_index = self._angle_between_points(index1, index2)

        # Check if thumbs and index fingertips are close enough
        if dist_thumb > self.thumb_threshold or dist_index > self.index_threshold:
            return False

        # Check angles - they should be roughly horizontal (close to 0 or 180 degrees)
        # Because hands form heart side-by-side, angles between the points should be similar
        if not (abs(angle_thumb) < self.angle_threshold or abs(angle_thumb - 180) < self.angle_threshold):
            return False
        if not (abs(angle_index) < self.angle_threshold or abs(angle_index - 180) < self.angle_threshold):
            return False

        # Optional: check if middle fingers are close to thumbs or index fingers to verify finger curl
        dist_middle_thumb1 = self._distance(middle1, thumb1)
        dist_middle_index1 = self._distance(middle1, index1)
        dist_middle_thumb2 = self._distance(middle2, thumb2)
        dist_middle_index2 = self._distance(middle2, index2)

        # If middle finger is far away (extended), likely not heart gesture
        if dist_middle_thumb1 > 60 and dist_middle_index1 > 60:
            return False
        if dist_middle_thumb2 > 60 and dist_middle_index2 > 60:
            return False

        # Passed all checks, detect heart gesture
        self.last_detection_time = now
        return True


def main():
    cap = cv.VideoCapture(0)
    detector = htm.handDetector(maxHands=2)
    heart_detector = HeartGestureDetector(thumb_threshold=40, index_threshold=40, cooldown=2.5)

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame")
            break

        img = cv.flip(img, 1)
        img = detector.findHands(img)

        # Check if 2 hands detected
        if detector.results.multi_hand_landmarks and len(detector.results.multi_hand_landmarks) == 2:
            lmList1 = detector.findPosition(img, handNo=0, draw=False)
            lmList2 = detector.findPosition(img, handNo=1, draw=False)

            if lmList1 and lmList2:
                if heart_detector.is_heart(lmList1, lmList2):
                    cv.putText(img, "Heart Gesture Detected! 🫶", (50, 100),
                               cv.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                    print("Heart Gesture Detected!")

        cv.imshow("Heart Gesture Detector", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
