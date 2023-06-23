import numpy as np
from collections import Counter
import cv2 as cv
import sys


# Le detecteur de code Aruco
det = cv.aruco.ArucoDetector()


# Affichage de fenetre
def display(title, img):
    cv.imshow(title, img)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()


# Recupere les 4 coins du plateau
def getBoardCorners(img):
    pts, ids, reject = det.detectMarkers(img)
    corners = []

    # On garde les coordonnees des Aruco dont l'id est 0
    for i in range(len(ids)):
        if ids[i][0] == 0:
            corners.append(pts[i][0].astype(int))


    # On trie les coordonnees pour avoir les Aruco en partant d'en haut a gauche dans le sens horaire

    # Tri horizontal
    for i in range(len(corners)):
        for j in range(len(corners)-i-1):
            if corners[j][0][0] > corners[j+1][0][0]: # s'il est + a droite, on swap
                aux = corners[j]
                corners[j] = corners[j+1]
                corners[j+1] = aux
    
    # Tri vertical
    if corners[0][0][1] > corners[1][0][1]: # s'il est + bas, on swap
        aux = corners[0]
        corners[0] = corners[1]
        corners[1] = aux

    if corners[2][0][1] > corners[3][0][1]:
        aux = corners[2]
        corners[2] = corners[3]
        corners[3] = aux

    # Arrangement final 
    aux = corners[1]
    corners[1] = corners[2]
    corners[2] = corners[3]
    corners[3] = aux

    # Seuls les coins du plateau nous interessent a present
    corners[0] = corners[0][0]
    corners[1] = corners[1][1]
    corners[2] = corners[2][2]
    corners[3] = corners[3][3]

    return corners


def inCaption(box):
    return (box[0][0] <= 230 and box[0][1] >= 375)


def detColor(img):
    display("Image d'origine", img)

    # On recupere les coins
    boardCorners = getBoardCorners(img)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [1125,5], [1125,745], [5,745]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1135,755))


    # On recupere les nouveaux coins
    boardCorners = getBoardCorners(img)
    display("Perspective corrigee", img)

    # Contours du plateau
    cv.polylines(img, np.array([boardCorners]), True, (0,0,255), 2)
    #display("Detection du plateau", img)


    # Etalonnage
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    cal = {"copper" : (hsv[400][30] - np.array([5, 40, 100]), hsv[400][30] + np.array([5, 40, 100])),
           "navy" : (hsv[483][187] - np.array([5, 40, 60]), hsv[483][187] + np.array([5, 40, 60])),
           "beige" : (hsv[422][116] - np.array([5, 40, 60]), hsv[422][116] + np.array([5, 40, 60])),
           "sky" : (hsv[490][117] - np.array([5, 40, 60]), hsv[490][117] + np.array([5, 40, 60])),
           "silver" : (hsv[472][27] - np.array([5, 40, 60]), hsv[472][27] + np.array([5, 5, 10])),
           "green" : (hsv[419][183] - np.array([5, 40, 60]), hsv[419][183] + np.array([5, 40, 60]))
            }
    # Pour chaque couleur : application de masque + detection de contours
    for col in cal:
        thresh = cv.inRange(hsv, cal[col][0], cal[col][1])

        # Reduction bruit hors contours puis dans contours
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        open = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        close = cv.morphologyEx(open, cv.MORPH_CLOSE, kernel)
        #display(col+" mask + noise reduction", close)

        contours = cv.findContours(close, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = contours[0]

        # Pour chaque contour : trouver le rectangle qui matche le mieux puis tous les dessiner
        sketch = img.copy()
        for c in contours:
            rot_rect = cv.minAreaRect(c)
            box = cv.boxPoints(rot_rect)
            box = np.int0(box)
            if not inCaption(box):
                cv.drawContours(sketch,[box],0,(0,255,0),2)
        
        display(col+" contours", sketch)



# Pour boucler sur toutes les images
dictImg =  {5: "img/photo/cube-1.png"} 



for k in dictImg: # Pour chaque image

    print("\n################\n")

    img = cv.imread(dictImg[k]) # Lecture de img
    print(dictImg[k])
    print("")

    detColor(img)
   
    

print("")    



