import cv2 as cv
import HandTrackingModule as htm

class GunGestureDetector:
    def __init__(self):
        pass

    def is_gun_gesture(self, lmList):
        if len(lmList) == 0:
            return False

        # Finger tip and pip landmark indices
        finger_tips = [4, 8, 12, 16, 20]
        finger_pips = [3, 6, 10, 14, 18]

        fingers = []

        # Thumb: For right hand, thumb tip x < pip x (extended)
        thumb_extended = lmList[4][1] < lmList[3][1] - 20  # with small tolerance
        fingers.append(1 if thumb_extended else 0)

        # Index finger: tip y < pip y => extended
        index_extended = lmList[8][2] < lmList[6][2] - 10
        fingers.append(1 if index_extended else 0)

        # Middle, ring, pinky: tip y > pip y => folded
        for tip, pip in zip(finger_tips[2:], finger_pips[2:]):
            folded = lmList[tip][2] > lmList[pip][2] + 10
            fingers.append(0 if folded else 1)  # append 0 if folded

        # Gun gesture = [1, 1, 0, 0, 0]
        return fingers == [1, 1, 1, 0, 0]

def main():
    cap = cv.VideoCapture(0)
    detector = htm.handDetector(detectionCon=0.7)
    gestureDetector = GunGestureDetector()

    while True:
        success, img = cap.read()
        img = cv.flip(img, 1)
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            if gestureDetector.is_gun_gesture(lmList):
                print("🔫 Gun Gesture Detected!")

        cv.imshow("Image", img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()
