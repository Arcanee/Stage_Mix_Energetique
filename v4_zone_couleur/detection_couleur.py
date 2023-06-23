import numpy as np
from collections import Counter
import cv2 as cv
import sys

# Surbrillance des codes ArUco
def displayBorder(im, pts):
    N = len(pts)
    for i in range(N):
        square = pts[i].astype(int)
        cv.polylines(im, [square], True, (188,255,5), 2) # Turquoise border
 
    # Affiche le resultat dans une fenêtre
    cv.imshow("Results", im)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()

colorList = { # in HSV  color space (opencv HSV ranges from (0,0,0) to (180,255,255))
	"red1" : (np.array([0, 25, 102]), np.array([4, 255, 255])), # red (first degrees)
	"red2" : (np.array([175, 25, 102]), np.array([180, 255, 255])), # red (last degrees)
	"yellow" : (np.array([27, 76, 178]), np.array([33, 255, 255])), # yellow
    "purple" : (np.array([125, 25, 51]), np.array([145, 255, 255])), # purple
    "orange" : (np.array([10, 76, 153]), np.array([15, 255, 255])), # orange
    "green" : (np.array([35, 25, 51]), np.array([60, 255, 255])), # green
    "blue" : (np.array([90, 38, 76]), np.array([115, 255, 255])) # blue
}

dictZone = {}
def checkColor(img, corner, ids):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    for i in range(len(corner)):
        coords = corner[i].astype(int)[0]
        id = ids[i][0]

        p1 = hsv[coords[0][1] - 5][coords[0][0] - 5] # diagonale de 5x5 pixels en haut à gauche de chaque coin
        p2 = hsv[coords[1][1] - 5][coords[1][0] - 5]
        p3 = hsv[coords[2][1] - 5][coords[2][0] - 5]
        p4 = hsv[coords[3][1] - 5][coords[3][0] - 5]

        red1 = colorList["red1"]
        red2 = colorList["red2"]
        green = colorList["green"]
        purple = colorList["purple"]
        yellow = colorList["yellow"]
        orange = colorList["orange"]
        blue = colorList["blue"]

        if ((p1 >= red1[0]).all() and (p1 <= red1[1]).all()) or ((p2 >= red1[0]).all() and (p2 <= red1[1]).all()) or ((p3 >= red1[0]).all() and (p3 <= red1[1]).all()) or ((p4 >= red1[0]).all() and (p4 <= red1[1]).all()):
            dictZone["Afrique"].append(id)
        elif ((p1 >= red2[0]).all() and (p1 <= red2[1]).all()) or ((p2 >= red2[0]).all() and (p2 <= red2[1]).all()) or ((p3 >= red2[0]).all() and (p3 <= red2[1]).all()) or ((p4 >= red2[0]).all() and (p4 <= red2[1]).all()):
            dictZone["Afrique"].append(id)
        elif ((p1 >= green[0]).all() and (p1 <= green[1]).all()) or ((p2 >= green[0]).all() and (p2 <= green[1]).all()) or ((p3 >= green[0]).all() and (p3 <= green[1]).all()) or ((p4 >= green[0]).all() and (p4 <= green[1]).all()):
            dictZone["Asie"].append(id)
        elif ((p1 >= purple[0]).all() and (p1 <= purple[1]).all()) or ((p2 >= purple[0]).all() and (p2 <= purple[1]).all()) or ((p3 >= purple[0]).all() and (p3 <= purple[1]).all()) or ((p4 >= purple[0]).all() and (p4 <= purple[1]).all()):
            dictZone["Oceanie"].append(id)
        elif ((p1 >= yellow[0]).all() and (p1 <= yellow[1]).all()) or ((p2 >= yellow[0]).all() and (p2 <= yellow[1]).all()) or ((p3 >= yellow[0]).all() and (p3 <= yellow[1]).all()) or ((p4 >= yellow[0]).all() and (p4 <= yellow[1]).all()):
            dictZone["Amerique du Nord / Groenland"].append(id)
        elif ((p1 >= blue[0]).all() and (p1 <= blue[1]).all()) or ((p2 >= blue[0]).all() and (p2 <= blue[1]).all()) or ((p3 >= blue[0]).all() and (p3 <= blue[1]).all()) or ((p4 >= blue[0]).all() and (p4 <= blue[1]).all()):
            dictZone["Europe"].append(id)
        elif ((p1 >= orange[0]).all() and (p1 <= orange[1]).all()) or ((p2 >= orange[0]).all() and (p2 <= orange[1]).all()) or ((p3 >= orange[0]).all() and (p3 <= orange[1]).all()) or ((p4 >= orange[0]).all() and (p4 <= orange[1]).all()):
            dictZone["Amerique du Sud"].append(id)
        else:
            print(id, ": X")
    print("")

# Pour boucler sur toutes les images
dictImg =  {0: "img/photo/risk-1.png",
            1: "img/photo/risk-2.png",
            2: "img/photo/risk-3.png",
            3: "img/photo/risk-4.png"}

# Pour les tests (plus rapide)
dictImgTest =  {41: "img/photo/zone-clean.png",
                2: "img/photo/zone-full.png",
                4: "img/photo/zone-angle.png"} 

# Pour donner un sentiment de reel dans l'affichage
dictCode = {0: "France",
            1: "Barrage",
            2: "Panneaux PV",
            3: "Centrale nucléaire",
            4: "Eolienne ON",
            5: "Eolienne OFF",
            6: "Methaniseur"}



# Le detecteur de code ArUco
det = cv.aruco.ArucoDetector()
dico = dictImg


for x in dico: # Pour chaque image

    dictZone = {"Amerique du Nord / Groenland" : [], "Amerique du Sud" : [],
                "Oceanie" : [], "Afrique" : [],
                "Europe" : [], "Asie" : []}


    print("\n################\n")

    img = cv.imread(dico[x]) # Lecture de img + detection des codes
    corner, id, reject = det.detectMarkers(img) # corner : les coordonnees, id : les donnees lues, reject : si un code est detecte mais donnee impossible a lire
    print(dico[x][10:])
    print("")

    if id is not None: # Si un code detecte
        c = Counter(np.sort(id.reshape(1,len(id))[0])) # Liste des elements de "id" avec leur nombre

        checkColor(img, corner, id)
        for k in dictZone:
            print(k, ":", dictZone[k])

        print("")
        displayBorder(img, corner)
        for y in c:
            print(dictCode[y], ":", c[y])  

        
    else: # Si aucun code detecte
        print("Aruco not detected")
        cv.imshow("Results", img)
        cv.waitKey(0) # Attente d'appui sur une touche
        cv.destroyAllWindows()
    
    

print("")    



