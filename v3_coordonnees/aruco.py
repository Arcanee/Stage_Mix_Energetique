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
    inBounds = 0 # origine
    for k in range(len(ids)):
        if ids[k][0] == 0:
            o = corner[k].astype(int)[0]
            inBounds = 1
            break
    if not inBounds:
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
dictImg =  {0: "img/photo/A3-7-clean.png",
            1: "img/photo/A3-7-clean-50p.png",
            2: "img/photo/A3-7-clean-30p.png",
            3: "img/photo/A3-15-clean.png",
            4: "img/photo/A3-15-clean-50p.png",
            5: "img/photo/A3-15-clean-30p.png",
            6: "img/photo/A3-15-lean.png",
            7: "img/photo/A3-15-lean-50p.png",
            8: "img/photo/A3-15-lean-30p.png",
            9: "img/photo/A3-15-lean-slight-rotate.png",
            10: "img/photo/A3-15-lean-slight-rotate-50p.png",
            11: "img/photo/A3-15-lean-slight-rotate-30p.png", # FAIL (30% de la taille + taille reduite a cause de l'inclinaison => trop petit)
            12: "img/photo/A3-15-lean-full-rotate.png",
            13: "img/photo/A3-15-lean-full-rotate-50p.png",
            14: "img/photo/A3-15-lean-full-rotate-30p.png", # FAIL (30% de la taille + taille reduite a cause de l'inclinaison => trop petit)
            15: "img/photo/A3-15-reverse.png",
            16: "img/photo/A3-15-reverse-50p.png",
            17: "img/photo/A3-15-reverse-30p.png",
            18: "img/photo/A3-15-reverse-slight-rotate.png",
            19: "img/photo/A3-15-reverse-slight-rotate-50p.png",
            20: "img/photo/A3-15-reverse-slight-rotate-30p.png", # FAIL (30% de la taille + taille reduite a cause de l'inclinaison => trop petit)
            21: "img/photo/A3-15-reverse-full-rotate.png",
            22: "img/photo/A3-15-reverse-full-rotate-50p.png",
            23: "img/photo/A3-15-reverse-full-rotate-30p.png", # FAIL (30% de la taille + taille reduite a cause de l'inclinaison => trop petit)
            24: "img/photo/reel-l1-i1.png",
            25: "img/photo/reel-l1-i1-far.png",
            26: "img/photo/reel-l1-i3.png",
            27: "img/photo/reel-l1-i3-far.png",
            28: "img/photo/reel-l2-i2-far.png",
            29: "img/photo/reel-l2-i3.png",
            30: "img/photo/reel-l3-i1-far.png",
            31: "img/photo/reel-l3-i2.png",
            32: "img/photo/reel-l3-i3.png",
            33: "img/photo/reel-l4-i1.png",
            34: "img/photo/reel-l4-i2.png",
            35: "img/photo/reel-l4-i2-bis.png",
            36: "img/photo/reel-l4-i2-far.png", # FAIL (trop loin / apparait trop petit)
            37: "img/photo/reel-l4-i3.png",
            38: "img/photo/reel-l4-i3-bis.png", # FAIL (1 code loin / petit / pas focus)
            39: "img/photo/reel-l0-i1.png", # FAIL (pas assez de lumiere)
            40: "img/photo/reel-l0-i2-far.png", # FAIL (pas assez de lumiere)
            41: "img/photo/size-test-l0-rotate.png", 
            42: "img/photo/size-test-l0-angle.png",
            43: "img/photo/size-test-l0-far.png",
            44: "img/photo/size-test.png",
            45: "img/photo/size-test-angle.png"}

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
dico = dictImgTest


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



