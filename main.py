import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)

canvas = None
xp, yp = 0, 0
brush_thickness = 15
eraser_thickness = 50

draw_color = (0, 255, 0)

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    if canvas is None:
        canvas = np.zeros_like(frame)

    hands, frame = detector.findHands(frame, draw=False)

    if hands:
        hand = hands[0]
        lmList = hand["lmList"]

        x1, y1 = int(lmList[8][0]), int(lmList[8][1])
        x2, y2 = int(lmList[12][0]), int(lmList[12][1])

        fingers = detector.fingersUp(hand)
        if fingers[1] and fingers[2]:
            cv2.circle(frame, (x1, y1), eraser_thickness // 2, (0, 0, 255), -1)
    
            if xp == 0 and yp == 0:
                xp, yp = x1, y1
            cv2.line(canvas, (xp, yp), (x1, y1), (0, 0, 0), eraser_thickness)
            xp, yp = x1, y1

        elif fingers[1] and not fingers[2]:
            cv2.circle(frame, (x1, y1), brush_thickness // 2, draw_color, -1)
            
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            cv2.line(canvas, (xp, yp), (x1, y1), draw_color, brush_thickness)
            xp, yp = x1, y1

        elif all(fingers[1:]):
            canvas = np.zeros_like(frame)
            cv2.putText(frame, "Canvas Cleared", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            xp, yp = 0, 0

        else:
            xp, yp = 0, 0
    else:
        xp, yp = 0, 0

    img_gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, img_inv = cv2.threshold(img_gray, 50, 255, cv2.THRESH_BINARY_INV)
    img_inv = cv2.cvtColor(img_inv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, img_inv)
    frame = cv2.bitwise_or(frame, canvas)

    cv2.imshow("Virtual Paint", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()