import numpy as np
import cv2 as cv
"""
import importlib.util
import sys
spec = importlib.util.spec_from_file_location("cv2", "/home/shinawi-/.local/lib/python3.9/site-packages/cv2/__init__.py")
cv = importlib.util.module_from_spec(spec)
sys.modules["cv2"] = cv
spec.loader.exec_module(cv)
"""

def displayBorder(im, pts):
    N = len(pts)
    for i in range(N):
        square = pts[i].astype(int)
        cv.polylines(im, [square], True, (255,0,0), 3)
 
    cv.imshow("Results", im)

det = cv.aruco.ArucoDetector()

img = cv.imread("img/aruco-0.png")
corner, id, reject = det.detectMarkers(img)

if id is not None:
    print("Decoded ids : {}".format(id))
    displayBorder(img, corner)
else:
    print("Aruco not detected")
    cv.imshow("Results", img)
 
cv.waitKey(0)
cv.destroyAllWindows()