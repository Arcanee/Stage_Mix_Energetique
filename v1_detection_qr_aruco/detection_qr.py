import numpy as np
import cv2 as cv


def displayBorder(im, pts):
    N = len(pts)
    for i in range(N):
        square = pts[i].astype(int)
        cv.polylines(im, [square], True, (255,0,0), 3)
 
    
    cv.imshow("Results", im)

det = cv.QRCodeDetector()

imgMulti = cv.imread("img/multi-distorded.png") # QR CODES NEED TO BE LARGE AND READABLE ENOUGH
retMulti, dataMulti, ptsMulti, qrMulti = det.detectAndDecodeMulti(imgMulti)

img = cv.imread("img/paca.png")
data, pts, qr = det.detectAndDecode(img)
ret = len(data)>0

if retMulti:
    print("Decoded Data : {}".format(dataMulti))
    displayBorder(imgMulti, ptsMulti)
else:
    print("QR Code not detected")
    cv.imshow("Results", imgMulti)
 
cv.waitKey(0)
cv.destroyAllWindows()