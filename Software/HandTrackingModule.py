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
    
    def findPosition(self,img, handNo=0 , draw=True):

        lmList = []
        if self.results.multi_hand_landmarks:
            myhand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myhand.landmark):
            # print(id,lm)
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                # print(id, lm)

                # print(id,cx, cy)

                lmList.append([id,cx,cy])
                if draw:
                    if id==4:
                        cv.circle(img, (cx,cy), 15 , (255,0,255) , cv.FILLED)

        return lmList

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