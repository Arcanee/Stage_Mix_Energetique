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


# Surbrillance des cercles
def highlightCircles(img, circles):
    for i in circles[0]:
            center = (i[0], i[1])
            radius = i[2]
            cv.circle(img, center, 1, (255, 0, 255), 2)
            cv.circle(img, center, radius, (255, 0, 255), 2)
 
    display("Detection des cercles", img)


def detCircles(img):

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 5)
    
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 30, param1=100, param2=18, minRadius=15, maxRadius=35)
    
    circles = np.uint16(np.around(circles))

    
    return circles


def weight(x, y, reg):
    regWeights = {"cor" : ((802,1118), (900,1067), (828,1056), (760,1050)),
                  "bre" : ((0,0), (220,585), (0,0), (0,0)),
                  "hdf" : ((504,397), (0,0), (0,0), (0,0)),
                  "occ" : ((464,1097), (418,1062), (527,1090), (590,1058)),}

    coords = regWeights[reg]
    dist = [sqrt((coords[0][0] - x)**2 + (coords[0][1] - y)**2),
            sqrt((coords[1][0]-x)**2 + (coords[1][1]-y)**2),
            sqrt((coords[2][0]-x)**2 + (coords[2][1]-y)**2),
            sqrt((coords[3][0]-x)**2 + (coords[3][1]-y)**2)]
    
    dmin = np.argmin(dist)
    corresp = [1, 2, 2, 5]

    return corresp[dmin]


def locate(coord, color):
    locImg = cv.imread("tests_A1/img/regions.png")
    hsv = cv.cvtColor(locImg, cv.COLOR_BGR2HSV)
    x = coord[0]
    y = coord[1]

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
            print("pion detecte en", reg, ", valeur :", weight(x, y, reg))


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

    # Contours (pour visualiser seulement)
    edges = cv.Canny(img, 80, 40)
    display("Detection des contours", edges)

    # Detection des cercles
    circles = detCircles(img)

    highlightCircles(img, circles)

    # Etalonnage couleurs cercles
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    cal = {}

    for c in circles[0]:
        #borderColor = hsv[c[1]+c[2]][c[0]]

        locate(c, "???")

    

    



# Pour boucler sur toutes les images
dictImg =  {0: "tests_A1/img/peinture.jpg"} 



for k in dictImg: # Pour chaque image

    print("\n################\n")

    img = cv.imread(dictImg[k]) # Lecture de img
    print(dictImg[k])
    print("")

    detColor(img)
   
    

print("")    



