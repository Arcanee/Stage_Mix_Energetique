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


# Surbrillance des cercles
def highlightCircles(img, circles):
    for i in circles[0]:
            center = (i[0], i[1])
            radius = i[2]
            cv.circle(img, center, 1, (0, 100, 100), 3)
            cv.circle(img, center, radius, (255, 0, 255), 3)
 
    display("Detection des cercles", img)


def detCircles(img):
    
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    gray = cv.medianBlur(gray, 5)
    
    circles = cv.HoughCircles(gray, cv.HOUGH_GRADIENT, 1, 30, param1=100, param2=30, minRadius=5, maxRadius=20)    
    
    circles = np.uint16(np.around(circles))

    
    return circles
    

def locate(coord, color):
    print("couleur", color, "detectee dans la zone [?]")

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
    display("Detection du plateau", img)

    # Contours (pour visualiser seulement)
    edges = cv.Canny(img, 80, 40)
    display("Detection des contours", edges)

    # Detection des cercles
    circles = detCircles(img)

    # Etalonnage
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    cal = {"green" : (hsv[155][45] - np.array([5, 40, 60]), hsv[155][45] + np.array([5, 40, 60])),
           "navy" : (hsv[210][45] - np.array([5, 40, 60]), hsv[210][45] + np.array([5, 40, 60])),
           "beige" : (hsv[270][45] - np.array([5, 40, 60]), hsv[270][45] + np.array([5, 40, 60])),
           "sky" : (hsv[335][45] - np.array([5, 40, 60]), hsv[335][45] + np.array([5, 40, 60])),
           "feutre_vert" : (hsv[146][42] - np.array([5, 40, 60]), hsv[146][42] + np.array([5, 40, 60])),
           "feutre_rouge" : (hsv[210][40] - np.array([5, 40, 60]), hsv[210][40] + np.array([5, 40, 60]))}

    for c in circles[0]:
        color = hsv[c[1]][c[0]]
        borderColor = hsv[c[1]+c[2]][c[0]]

        if (color >= cal["green"][0]).all() and (color <= cal["green"][1]).all():
            locate(c, "green")
        elif (color >= cal["navy"][0]).all() and (color <= cal["navy"][1]).all():
            locate(c, "navy")
        elif (color >= cal["beige"][0]).all() and (color <= cal["beige"][1]).all():
            locate(c, "beige")
        elif (color >= cal["sky"][0]).all() and (color <= cal["sky"][1]).all():
            locate(c, "sky")
        elif (borderColor >= cal["feutre_vert"][0]).all() and (borderColor <= cal["feutre_vert"][1]).all():
            locate(c, "feutre_vert")
        elif (borderColor >= cal["feutre_rouge"][0]).all() and (borderColor <= cal["feutre_rouge"][1]).all():
            locate(c, "feutre_rouge")
        else:
            print("couleur non reconnue")
            #raise Exception("couleur non reconnue")

    

    highlightCircles(img, circles)



# Pour boucler sur toutes les images
dictImg =  {5: "img/photo/cercle-4.png",
            1: "img/photo/cercle-5.png"} 



for k in dictImg: # Pour chaque image

    print("\n################\n")

    img = cv.imread(dictImg[k]) # Lecture de img
    print(dictImg[k])
    print("")

    detColor(img)
   
    

print("")    



