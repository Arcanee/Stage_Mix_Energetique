import numpy as np
from collections import Counter
import cv2 as cv
import sys


# Affichage de fenetre
def display(title, img):
    cv.imshow(title, img)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()


# Surbrillance des Aruco
def highlightAruco(img, pts, ids):
    N = len(pts)
    for i in range(N):
        if ids[i][0] != 0:
            square = pts[i].astype(int)
            cv.polylines(img, [square], True, (255,0,0), 2)
 
    display("Codes reperes", img)


# Recupere les 4 coins du plateau
def getBoardCorners(img):
    pts, ids, reject = det.detectMarkers(img)
    corners = []

    # On garde les coordonnees des Aruco dont l'id est 0
    for i in range(len(ids)):
        if ids[i][0] == 0:
            corners.append(pts[i][0].astype(int))


    # On trie les coordonnees pour avoir les Arucoen partant d'en haut a gauche dans le sens horaire

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

dictZone = {}
def locateAruco(img):
    display("Image d'origine", img)

    # On recupere les coins
    boardCorners = getBoardCorners(img)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [1125,5], [1125,745], [5,745]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1135,755))

    display("Perspective corrigee", img)

    # Detection des Aruco
    pts, ids, reject = det.detectMarkers(img)

    # On recupere les nouveaux coins
    boardCorners = getBoardCorners(img)
    
    vxTop = ((boardCorners[1] - boardCorners[0]) / 100).astype(int)
    vxBot = ((boardCorners[2] - boardCorners[3]) / 100).astype(int)
    vyLeft = ((boardCorners[3] - boardCorners[0]) / 100).astype(int)
    vyRight = ((boardCorners[2] - boardCorners[1]) / 100).astype(int)

    # Contour du plateau
    cv.polylines(img, np.array([boardCorners]), True, (0,0,255), 2)

    # Definition des zones
    MER_AM_AF = 42
    MER_AF_OC = 70
    MER_AF_AS = 59
    MER_EU_AS = 64

    PAR_N_S = 57
    PAR_AS_OC = 70

    # Delimitation verticales
    cv.line(img, boardCorners[0]+MER_AM_AF*vxTop, boardCorners[3]+MER_AM_AF*vxBot, (0,0,255), 2)
    cv.line(img, boardCorners[0]+MER_AF_OC*vxTop, boardCorners[3]+MER_AF_OC*vxBot, (0,0,255), 2)
    cv.line(img, boardCorners[0]+MER_EU_AS*vxTop, boardCorners[3]+MER_EU_AS*vxBot, (0,0,255), 2)
    cv.line(img, boardCorners[0]+MER_AF_AS*vxTop, boardCorners[3]+MER_AF_AS*vxBot, (0,0,255), 2)

    # Delimitation horizontales
    cv.line(img, boardCorners[0]+PAR_N_S*vyLeft, boardCorners[1]+PAR_N_S*vyRight, (0,0,255), 2)
    cv.line(img, boardCorners[0]+PAR_AS_OC*vyLeft, boardCorners[1]+PAR_AS_OC*vyRight, (0,0,255), 2)

    display("Zones definies", img)

    # Mapping des Aruco dans les differentes zones
    for i in range(len(ids)):
        id = ids[i][0]
        pt = pts[i][0].astype(int)[0] # On regarde un seul point pour simplifier la tache
        
        if id != 0:
            # OUEST
            if pt[0] < (boardCorners[0]+MER_AM_AF*vxTop)[0]:
                # NORD
                if pt[1] < (boardCorners[0]+PAR_N_S*vyLeft)[1]:
                    dictZone["Amerique du Nord"].append(id)
                # SUD
                else:
                    dictZone["Amerique du Sud"].append(id)
            
            # SINON (EST), SI NORD
            elif pt[1] < (boardCorners[0]+PAR_N_S*vyLeft)[1]:
                # OUEST
                if pt[0] < (boardCorners[0]+MER_EU_AS*vxTop)[0]:
                    dictZone["Europe"].append(id)
                # EST
                else:
                    dictZone["Asie"].append(id)
            
            # SINON (SUD), SI OUEST
            elif pt[0] < (boardCorners[0]+MER_AF_AS*vxTop)[0]:
                dictZone["Afrique"].append(id)
            
            # SINON (CENTRE / EST), SI NORD DE L'OCEANIE
            elif pt[1] < (boardCorners[0]+PAR_AS_OC*vyLeft)[1]:
                dictZone["Asie"].append(id)

            # SINON (SUD DE L'ASIE), SI OUEST
            elif pt[0] < (boardCorners[0]+MER_AF_OC*vxTop)[0]:
                dictZone["Afrique"].append(id)
                
            # SINON (PLEIN SUD-EST)
            else:
                dictZone["Oceanie"].append(id)

    for k in dictZone:
        print(k, ":", dictZone[k])

    highlightAruco(img, pts, ids)



# Pour boucler sur toutes les images
dictImg =  {0: "img/photo/risk-1.png",
            4: "img/photo/risk-2.png",
            2: "img/photo/risk-3.png",
            1 : "img/photo/risk-4.png"} 

# Pour donner un sentiment de reel dans l'affichage
dictCode = {0: "France",
            1: "Barrage",
            2: "Panneaux PV",
            3: "Centrale nucléaire",
            4: "Eolienne ON",
            5: "Eolienne OFF",
            6: "Methaniseur"}


# Le detecteur de code Aruco
det = cv.aruco.ArucoDetector()
dico = dictImg


for k in dico: # Pour chaque image

    # Liste des IDs contenus dans chaque zone
    dictZone = {"Amerique du Nord": [], "Amerique du Sud": [], "Asie": [],
                "Afrique": [], "Oceanie": [], "Europe": []}

    print("\n################\n")

    img = cv.imread(dico[k]) # Lecture de img
    print(dico[k][10:])
    print("")

    locateAruco(img)
   
    

print("")    



