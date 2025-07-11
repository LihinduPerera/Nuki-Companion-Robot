import cv2 as cv 
import mediapipe as mp
import time

class handDetector():
    def __init__(self,mode=False,maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
    )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        # img = cv.flip(img, 1) # Flip the image to the correct direction
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                                self.mpHands.HAND_CONNECTIONS)
        return img
    
    def findPosition(self, img, handNo=0, draw=True, returnZ=False):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            h, w, _ = img.shape
            for id, lm in enumerate(myHand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                if returnZ:
                    self.lmList.append([id, lm.x, lm.y, lm.z])  # z included
                else:
                    self.lmList.append([id, cx, cy])
                if draw:
                    cv.circle(img, (cx, cy), 5, (255, 0, 0), cv.FILLED)
        return self.lmList


def main():
    previousTime = 0 
    currentTime = 0

    cap  = cv.VideoCapture(0)
    detector = handDetector()

    while True:
        success, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        if len(lmList) !=0:
            print(lmList[4])

        currentTime = time.time()
        fps = 1/(currentTime-previousTime)
        previousTime = currentTime

        cv.putText(img, str(int(fps)), (10,70) , cv.FONT_HERSHEY_PLAIN, 3 , (255,0,255), 3)


        cv.imshow("Image" , img)
        cv.waitKey(1)

if __name__ == "__main__":
    main()