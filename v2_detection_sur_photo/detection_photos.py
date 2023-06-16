import numpy as np
from collections import Counter
import cv2 as cv

# Surbrillance des codes ArUco
def display(im, pts):
    N = len(pts)
    for i in range(N):
        square = pts[i].astype(int)
        cv.polylines(im, [square], True, (255,0,0), 3)
 
    # Affiche le resultat dans une fenêtre
    cv.imshow("Results", im)


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
dictImgTest =  {39: "img/photo/size-test-l0-rotate.png", 
            40: "img/photo/size-test-l0-angle.png",
            1: "img/photo/size-test-l0-far.png",
            2: "img/photo/TEST.png"} 

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

    print("\n################\n")

    img = cv.imread(dico[x]) # Lecture de img + detection des codes
    corner, id, reject = det.detectMarkers(img) # corner : les coordonnees, id : les donnees lues, reject : si un code est detecte mais donnee impossible a lire
    print(dico[x][10:])
    print("")

    if id is not None: # Si un code detecte
        c = Counter(np.sort(id.reshape(1,len(id))[0])) # Liste des elements de "id" avec leur nombre
        display(img, corner)
        for y in c:
            print(dictCode[y], ":", c[y])
        
    else: # Si aucun code detecte
        print("Aruco not detected")
        cv.imshow("Results", img)
    
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()

print("")    


