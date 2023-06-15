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

colorList = { # in HSV  color space (opencv HSV ranges from (0,0,0) to (180,255,255))
	"red" : (np.array([0, 204, 204]), np.array([5, 255, 255])), # red
	"magenta" : (np.array([148, 204, 204]), np.array([165, 255, 255])), # magenta
	"green" : (np.array([45, 204, 204]), np.array([60, 255, 255])), # green
    "purple" : (np.array([135, 204, 204]), np.array([140, 255, 255])), # purple
    "brown" : (np.array([8, 204, 41]), np.array([18, 255, 153])), # brown
    "yellow" : (np.array([25, 204, 204]), np.array([30, 255, 255])), # yellow
    "bordeaux" : (np.array([0, 204, 102]), np.array([5, 255, 153])), # bordeaux
    "beige" : (np.array([6, 115, 204]), np.array([17, 178, 255])), # beige
    "pink" : (np.array([0, 76, 204]), np.array([5, 178, 255])), # pink
    "orange" : (np.array([6, 204, 204]), np.array([20, 255, 255])), # orange
    "cyan" : (np.array([80, 153, 204]), np.array([90, 255, 255])), # cyan
    "blue" : (np.array([110, 204, 76]), np.array([125, 255, 255])) # blue
}

def checkColor(img, corner, ids):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    for i in range(len(corner)):
        coords = corner[i].astype(int)[0]
        id = ids[i][0]

        p1 = hsv[coords[0][1] - 5][coords[0][0] - 5] # diagonale de 5x5 pixels en haut à gauche de chaque coin
        p2 = hsv[coords[1][1] - 5][coords[1][0] - 5]
        p3 = hsv[coords[2][1] - 5][coords[2][0] - 5]
        p4 = hsv[coords[3][1] - 5][coords[3][0] - 5]

        red = colorList["red"]
        magenta = colorList["magenta"]
        green = colorList["green"]
        purple = colorList["purple"]
        brown = colorList["brown"]
        yellow = colorList["yellow"]
        bordeaux = colorList["bordeaux"]
        beige = colorList["beige"]
        pink = colorList["pink"]
        orange = colorList["orange"]
        cyan = colorList["cyan"]
        blue = colorList["blue"]

        if ((p1 >= red[0]).all() and (p1 <= red[1]).all()) or ((p2 >= red[0]).all() and (p2 <= red[1]).all()) or ((p3 >= red[0]).all() and (p3 <= red[1]).all()) or ((p4 >= red[0]).all() and (p4 <= red[1]).all()):
            print("l'id {} est dans une zone rouge".format(id))
        elif ((p1 >= magenta[0]).all() and (p1 <= magenta[1]).all()) or ((p2 >= magenta[0]).all() and (p2 <= magenta[1]).all()) or ((p3 >= magenta[0]).all() and (p3 <= magenta[1]).all()) or ((p4 >= magenta[0]).all() and (p4 <= magenta[1]).all()):
            print("l'id {} est dans une zone magenta".format(id))
        elif ((p1 >= green[0]).all() and (p1 <= green[1]).all()) or ((p2 >= green[0]).all() and (p2 <= green[1]).all()) or ((p3 >= green[0]).all() and (p3 <= green[1]).all()) or ((p4 >= green[0]).all() and (p4 <= green[1]).all()):
            print("l'id {} est dans une zone verte".format(id))
        elif ((p1 >= purple[0]).all() and (p1 <= purple[1]).all()) or ((p2 >= purple[0]).all() and (p2 <= purple[1]).all()) or ((p3 >= purple[0]).all() and (p3 <= purple[1]).all()) or ((p4 >= purple[0]).all() and (p4 <= purple[1]).all()):
            print("l'id {} est dans une zone violette".format(id))
        elif ((p1 >= brown[0]).all() and (p1 <= brown[1]).all()) or ((p2 >= brown[0]).all() and (p2 <= brown[1]).all()) or ((p3 >= brown[0]).all() and (p3 <= brown[1]).all()) or ((p4 >= brown[0]).all() and (p4 <= brown[1]).all()):
            print("l'id {} est dans une zone marron".format(id))
        elif ((p1 >= yellow[0]).all() and (p1 <= yellow[1]).all()) or ((p2 >= yellow[0]).all() and (p2 <= yellow[1]).all()) or ((p3 >= yellow[0]).all() and (p3 <= yellow[1]).all()) or ((p4 >= yellow[0]).all() and (p4 <= yellow[1]).all()):
            print("l'id {} est dans une zone jaune".format(id))
        elif ((p1 >= bordeaux[0]).all() and (p1 <= bordeaux[1]).all()) or ((p2 >= bordeaux[0]).all() and (p2 <= bordeaux[1]).all()) or ((p3 >= bordeaux[0]).all() and (p3 <= bordeaux[1]).all()) or ((p4 >= bordeaux[0]).all() and (p4 <= bordeaux[1]).all()):
            print("l'id {} est dans une zone bordeaux".format(id))
        elif ((p1 >= beige[0]).all() and (p1 <= beige[1]).all()) or ((p2 >= beige[0]).all() and (p2 <= beige[1]).all()) or ((p3 >= beige[0]).all() and (p3 <= beige[1]).all()) or ((p4 >= beige[0]).all() and (p4 <= beige[1]).all()):
            print("l'id {} est dans une zone beige".format(id))
        elif ((p1 >= pink[0]).all() and (p1 <= pink[1]).all()) or ((p2 >= pink[0]).all() and (p2 <= pink[1]).all()) or ((p3 >= pink[0]).all() and (p3 <= pink[1]).all()) or ((p4 >= pink[0]).all() and (p4 <= pink[1]).all()):
            print("l'id {} est dans une zone rose".format(id))
        elif ((p1 >= orange[0]).all() and (p1 <= orange[1]).all()) or ((p2 >= orange[0]).all() and (p2 <= orange[1]).all()) or ((p3 >= orange[0]).all() and (p3 <= orange[1]).all()) or ((p4 >= orange[0]).all() and (p4 <= orange[1]).all()):
            print("l'id {} est dans une zone orange".format(id))
        elif ((p1 >= cyan[0]).all() and (p1 <= cyan[1]).all()) or ((p2 >= cyan[0]).all() and (p2 <= cyan[1]).all()) or ((p3 >= cyan[0]).all() and (p3 <= cyan[1]).all()) or ((p4 >= cyan[0]).all() and (p4 <= cyan[1]).all()):
            print("l'id {} est dans une zone cyan".format(id))
        elif ((p1 >= blue[0]).all() and (p1 <= blue[1]).all()) or ((p2 >= blue[0]).all() and (p2 <= blue[1]).all()) or ((p3 >= blue[0]).all() and (p3 <= blue[1]).all()) or ((p4 >= blue[0]).all() and (p4 <= blue[1]).all()):
            print("l'id {} est dans une zone bleue".format(id))
        else:
            print("l'id {} n'est reconnu dans aucune zone".format(id))

# Pour boucler sur toutes les images
dictImg =  {0: "img/photo/color-test.png"}

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

    print("\n################\n")

    img = cv.imread(dico[x]) # Lecture de img + detection des codes
    corner, id, reject = det.detectMarkers(img) # corner : les coordonnees, id : les donnees lues, reject : si un code est detecte mais donnee impossible a lire
    print(dico[x][10:])
    print("")

    if id is not None: # Si un code detecte
        c = Counter(np.sort(id.reshape(1,len(id))[0])) # Liste des elements de "id" avec leur nombre

        checkColor(img, corner, id)

        displayBorder(img, corner)
        for y in c:
            print(dictCode[y], ":", c[y])  

        
    else: # Si aucun code detecte
        print("Aruco not detected")
        cv.imshow("Results", img)
        cv.waitKey(0) # Attente d'appui sur une touche
        cv.destroyAllWindows()
    
    

print("")    



