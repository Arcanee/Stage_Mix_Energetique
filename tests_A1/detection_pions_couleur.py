import numpy as np
from collections import Counter
import cv2 as cv
import sys
from math import sqrt


# Affichage de fenetre
def display(title, img):
    cv.imshow(title, img)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()


# Localise la region
def locate(box, color):
    locImg = cv.imread("tests_A1/img/regions.png")
    hsv = cv.cvtColor(locImg, cv.COLOR_BGR2HSV)
    x = box[0][0]
    y = box[0][1]

    # Couleur par region
    cal = {"hdf" : (hsv[350][500] - np.array([2, 20, 20]), hsv[350][500] + np.array([2, 20, 20])),
           "idf" : (hsv[500][500] - np.array([2, 20, 20]), hsv[500][500] + np.array([2, 20, 20])),
           "bre" : (hsv[500][100] - np.array([2, 20, 20]), hsv[500][100] + np.array([2, 20, 20])),
           "pll" : (hsv[700][200] - np.array([2, 20, 20]), hsv[700][200] + np.array([2, 20, 20])),
           "cvl" : (hsv[700][500] - np.array([2, 20, 20]), hsv[700][500] + np.array([2, 20, 20])),
           "bfc" : (hsv[500][800] - np.array([2, 20, 20]), hsv[500][800] + np.array([2, 20, 20])),
           "pac" : (hsv[800][800] - np.array([2, 20, 20]), hsv[800][800] + np.array([2, 20, 20])),
           "occ" : (hsv[1000][500] - np.array([2, 20, 20]), hsv[1000][500] + np.array([2, 20, 20])),
           "naq" : (hsv[1000][200] - np.array([2, 20, 20]), hsv[1000][200] + np.array([2, 20, 20])),
           "est" : (hsv[300][800] - np.array([2, 20, 20]), hsv[300][800] + np.array([2, 20, 20])),
           "ara" : (hsv[700][700] - np.array([2, 20, 20]), hsv[700][700] + np.array([2, 20, 20])),
           "nor" : (hsv[300][300] - np.array([2, 20, 20]), hsv[300][300] + np.array([2, 20, 20])),
           "cor" : (hsv[1000][800] - np.array([2, 20, 20]), hsv[1000][800] + np.array([2, 20, 20]))}
    
    for reg in cal:
        if (hsv[y][x] >= cal[reg][0]).all() and (hsv[y][x] <= cal[reg][1]).all():
            print("{} soldier in {}".format(color, reg))


# Renvoie vrai si fait partie de la légende
def inRegions(box):
    return (box[2][1] <= 1154 and box[0][1] >= 207)

# Recupere les 4 coins du plateau
def getBoardCorners(img):
    # Le detecteur de code Aruco
    det = cv.aruco.ArucoDetector()

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


# Detecte les pions grace a leur couleur
def detColor(img):
    display("Image d'origine", img)

    # On recupere les coins
    boardCorners = getBoardCorners(img)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [995,5], [995,1195], [5,1195]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1000,1200))
    

    # On recupere les nouveaux coins
    boardCorners = getBoardCorners(img)
    display("Perspective corrigee", img)

    # Contours du plateau
    cv.polylines(img, np.array([boardCorners]), True, (0,0,255), 2)
    display("Detection du plateau", img)



    # Etalonnage
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    cal = {"blue" : (hsv[35][83] - np.array([5, 100, 100]), hsv[35][83] + np.array([5, 100, 100])),
           "green" : (hsv[53][170] - np.array([5, 100, 100]), hsv[53][170] + np.array([5, 100, 100])),
           "orange" : (hsv[71][85] - np.array([5, 100, 100]), hsv[71][85] + np.array([5, 100, 100])),
           "yellow" : (hsv[83][136] - np.array([5, 100, 100]), hsv[83][136] + np.array([5, 100, 100])),
           "black" : (hsv[40][128] - np.array([180, 255, 30]), hsv[40][128] + np.array([180, 255, 30]))
            }
    
    # Pour chaque couleur : application de masque + detection de contours
    for col in cal:
        thresh = cv.inRange(hsv, cal[col][0], cal[col][1])

        # Reduction bruit hors contours puis dans contours
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        open = cv.morphologyEx(thresh, cv.MORPH_OPEN, kernel)
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        close = cv.morphologyEx(open, cv.MORPH_CLOSE, kernel)
        display(col+" mask + noise reduction", close)

        contours = cv.findContours(close, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = contours[0]

        # Pour chaque contour : trouver le rectangle qui matche le mieux puis tous les dessiner
        sketch = img.copy()
        for c in contours:        
            rot_rect = cv.minAreaRect(c)
            box = cv.boxPoints(rot_rect)
            box = np.int0(box)
            if inRegions(box):
                cv.drawContours(sketch,[box],0,(0,255,0),2)
                locate(box, col)

        #cv.imwrite("{}.png".format(col), sketch)
        display("boxes", sketch)

    

    



# Pour boucler sur toutes les images
dictImg =  {0: "tests_A1/img/soldiers.jpg"} 



for k in dictImg: # Pour chaque image

    print("\n################\n")

    img = cv.imread(dictImg[k]) # Lecture de img
    print(dictImg[k])
    print("")

    detColor(img)
   
    

print("")    



