import cv2
import numpy as np


def empty(a):
    pass


cap = cv2.VideoCapture(2)
cap.set(3, 640)
cap.set(4, 480)

totalMoney = 0


def preProcessing(img):
    imgPre = cv2.GaussianBlur(img, (7, 7), 5)

    imgPre = cv2.Canny(imgPre, 0, 215)
    kernel = np.ones((3, 3), np.uint8)
    imgPre = cv2.dilate(imgPre, kernel, iterations=2)

    imgPre = cv2.morphologyEx(imgPre, cv2.MORPH_CLOSE, kernel)
    return imgPre


def findContours(img, imgPre, minArea, maxArea=10000, sort=True, filter=0, drawCon=True, c=(255, 0, 0)):
    conFound = []
    imgContours = img.copy()
    contours, hierarchy = cv2.findContours(imgPre, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > minArea and area < maxArea:
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
            # print(len(approx))
            if len(approx) == filter or filter == 0:
                if drawCon: cv2.drawContours(imgContours, cnt, -1, c, 3)
                x, y, w, h = cv2.boundingRect(approx)
                cx, cy = x + (w // 2), y + (h // 2)

                cv2.rectangle(imgContours, (x, y), (x + w, y + h), c, 2)
                cv2.circle(imgContours, (x + (w // 2), y + (h // 2)), 5, c, cv2.FILLED)
                conFound.append({"cnt": cnt, "area": area, "bbox": [x, y, w, h], "center": [cx, cy]})

    if sort:
        conFound = sorted(conFound, key=lambda x: x["area"], reverse=True)

    return imgContours, conFound


while True:
    totalMoney = 0
    success, img = cap.read()
    imgPre = preProcessing(img)
    minArea = cv2.getTrackbarPos("Min Area", "Settings")
    imgContours, contoursFound = findContours(img, imgPre, 0)

    if contoursFound:
        for contour in contoursFound:
            peri = cv2.arcLength(contour['cnt'], True)
            approx = cv2.approxPolyDP(contour['cnt'], 0.02 * peri, True)

            if len(approx > 5):

                centerx, centery = contour['center']

                #cv2.circle(imgContours, (centerx - 15, centery + 15), 5, (255, 255, 255), thickness=1)

                try:
                    pixel_color = img[centerx - 15, centery + 15]
                except:
                    pass

                pixel_color = [pixel_color[i] for i in [2, 1, 0]]
                penny_min = np.array([79, 69, 0])
                penny_max = np.array([255, 113, 61])

                area = contour["area"]

                """print((penny_min <= pixel_color).all() and (pixel_color <= penny_max).all())
                print(area)
                print(pixel_color)"""

                isPenny = (penny_min <= pixel_color).all() and (pixel_color <= penny_max).all()
                if area < 4000 and not isPenny:
                    totalMoney += 10
                elif area < 5300 or isPenny:
                    totalMoney += 1
                elif area < 6000 and not isPenny:
                    totalMoney += 5
                elif area > 6000 and not isPenny:
                    totalMoney += 25

    if totalMoney < 100:
        text = f'{totalMoney} Cents'
    else:
        text = f'${totalMoney / 100:.2f}'
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    thickness = 2

    textSize, _ = cv2.getTextSize(text, font, fontScale, thickness)
    x, y = 400, 50

    cv2.rectangle(imgContours, (x, y), (x + textSize[0], y + textSize[1]), (255, 255, 255), cv2.FILLED)
    cv2.putText(imgContours, text, (x, y + textSize[1]), font, fontScale, (0, 0, 0), thickness)

    cv2.imshow("images", imgContours)
    cv2.waitKey(1)

