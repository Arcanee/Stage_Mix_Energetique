import numpy as np
from collections import Counter
import cv2 as cv
import sys

# Surbrillance des codes ArUco
def displayBorder(im, pts):
    N = len(pts)
    for i in range(N):
        square = pts[i].astype(int)
        cv.polylines(im, [square], True, (255,0,0), 2)
 
    # Affiche le resultat dans une fenêtre
    cv.imshow("Results", im)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()


dictZone = {}
def detectZone(corner, ids, img):
    regionOK = 0 # origine
    for k in range(len(ids)):
        if ids[k][0] == 0:
            o = corner[k].astype(int)[0]
            regionOK = 1
            break
    if not regionOK:
        sys.exit("Pas de region detectee\n")

    vx = o[1] - o[0]
    vy = o[2] - o[1]

    cv.line(img, o[0], o[0]+15*vx, (0,0,255), 2)
    cv.line(img, o[0]+7*vy, o[0]+7*vy+15*vx, (0,0,255), 2)
    cv.line(img, o[0]+14*vy, o[0]+14*vy+15*vx, (0,0,255), 2)
    cv.line(img, o[0]+21*vy, o[0]+21*vy+15*vx, (0,0,255), 2)

    cv.line(img, o[0], o[0]+21*vy, (0,0,255), 2)
    cv.line(img, o[0]+5*vx, o[0]+5*vx+21*vy, (0,0,255), 2)
    cv.line(img, o[0]+10*vx, o[0]+10*vx+21*vy, (0,0,255), 2)
    cv.line(img, o[0]+15*vx, o[0]+15*vx+21*vy, (0,0,255), 2)
 
    # Affiche le resultat dans une fenêtre
    cv.imshow("Borders", img)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()

    for i in range(len(corner)):
        coords = corner[i].astype(int)[0]
        id = ids[i][0]

        if id != 0:

            if (coords[0][1] > o[0][1]).all() and (coords[2][1] < (6*vy + o[2])[1]).all(): # 1ere ligne
                L = 0
            elif (coords[0][1] > o[0][1]).all() and (coords[2][1] < (13*vy + o[2])[1]).all(): # 2e
                L = 1
            elif (coords[0][1] > o[0][1]).all() and (coords[2][1] < (20*vy + o[2])[1]).all(): # 3e
                L = 2
            else:
                sys.exit("code hors limite ({})\n".format(dictCode[id]))

            if (coords[0][0] > o[0][0]).all() and (coords[1][0] < (4*vx + o[1])[0]).all(): # 1ere colonne
                C = 0
            elif (coords[0][0] > o[0][0]).all() and (coords[1][0] < (9*vx + o[1])[0]).all(): # 2e
                C = 1
            elif (coords[0][0] > o[0][0]).all() and (coords[1][0] < (14*vx + o[1])[0]).all(): # 3e
                C = 2
            else:
                sys.exit("code hors limite ({})\n".format(dictCode[id]))

            if L == 0 and C == 0:
                zone = "A"
            elif L == 0 and C == 1:
                zone = "B"
            elif L == 0 and C == 2:
                zone = "C"
            elif L == 1 and C == 0:
                zone = "D"
            elif L == 1 and C == 1:
                zone = "E"
            elif L == 1 and C == 2:
                zone = "F"
            elif L == 2 and C == 0:
                zone = "G"
            elif L == 2 and C == 1:
                zone = "H"
            elif L == 2 and C == 2:
                zone = "I"

            dictZone[zone].append(dictCode[id])

            



# Pour boucler sur toutes les images
dictImg =  {41: "img/photo/zone-clean.png",
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

    # Liste des IDs contenus dans chaque zone
    dictZone = {"A": [], "B": [], "C": [],
                "D": [], "E": [], "F": [],
                "G": [], "H": [], "I": [],}

    print("\n################\n")

    img = cv.imread(dico[x]) # Lecture de img + detection des codes
    corner, id, reject = det.detectMarkers(img) # corner : les coordonnees, id : les donnees lues, reject : si un code est detecte mais donnee impossible a lire
    print(dico[x][10:])
    print("")

    if id is not None: # Si un code detecte
        c = Counter(np.sort(id.reshape(1,len(id))[0])) # Liste des elements de "id" avec leur nombre
        displayBorder(img, corner)
        for y in c:
            print(dictCode[y], ":", c[y])

        detectZone(corner, id, img)
        for zone in dictZone:
            print(zone, ":", dictZone[zone])
        
    else: # Si aucun code detecte
        print("Aruco not detected")
        cv.imshow("Results", img)
        cv.waitKey(0) # Attente d'appui sur une touche
        cv.destroyAllWindows()
    
    

print("")    



