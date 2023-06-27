import numpy as np
from collections import Counter
import cv2 as cv
import sys
import json


# Affichage de fenetre
def display(title, img):
    pass
    #cv.imshow(title, img)
    #cv.waitKey(0) # Attente d'appui sur une touche
    #cv.destroyAllWindows()


# Surbrillance des Aruco
def highlightAruco(img, pts, ids):
    N = len(pts)
    for i in range(N):
        if ids[i][0] != 0:
            square = pts[i].astype(int)
            cv.polylines(img, [square], True, (255,0,0), 2)
 
    display("Codes reperes", img)


# Recupere les 4 coins du plateau
def getBoardCorners(img, det):
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


def locateAruco(img, det, dictZone):
    display("Image d'origine", img)

    # On recupere les coins
    boardCorners = getBoardCorners(img, det)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [1125,5], [1125,745], [5,745]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1135,755))

    display("Perspective corrigee", img)

    # Detection des Aruco
    pts, ids, reject = det.detectMarkers(img)

    # On recupere les nouveaux coins
    boardCorners = getBoardCorners(img, det)
    
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

        if id == 0:
            dictZone["Carte"] = 0
        
        if id != 0:
            # OUEST
            if pt[0] < (boardCorners[0]+MER_AM_AF*vxTop)[0]:
                # NORD
                if pt[1] < (boardCorners[0]+PAR_N_S*vyLeft)[1]:
                    dictZone["AN"].append(int(id))
                # SUD
                else:
                    dictZone["AS"].append(int(id))
            
            # SINON (EST), SI NORD
            elif pt[1] < (boardCorners[0]+PAR_N_S*vyLeft)[1]:
                # OUEST
                if pt[0] < (boardCorners[0]+MER_EU_AS*vxTop)[0]:
                    dictZone["Europe"].append(int(id))
                # EST
                else:
                    dictZone["Asie"].append(int(id))
            
            # SINON (SUD), SI OUEST
            elif pt[0] < (boardCorners[0]+MER_AF_AS*vxTop)[0]:
                dictZone["Afrique"].append(int(id))
            
            # SINON (CENTRE / EST), SI NORD DE L'OCEANIE
            elif pt[1] < (boardCorners[0]+PAR_AS_OC*vyLeft)[1]:
                dictZone["Asie"].append(int(id))

            # SINON (SUD DE L'ASIE), SI OUEST
            elif pt[0] < (boardCorners[0]+MER_AF_OC*vxTop)[0]:
                dictZone["Afrique"].append(int(id))
                
            # SINON (PLEIN SUD-EST)
            else:
                dictZone["Oceanie"].append(int(id))

    highlightAruco(img, pts, ids)




def coord_main():
    #Liste des zones
    dictZone = {"AN": [], "AS": [], "Asie": [],
                        "Afrique": [], "Oceanie": [], "Europe": [], "Carte": ""}

    # Pour boucler sur toutes les images
    dictImg =  {0: "image.png"} 

    # Pour donner un sentiment de reel dans l'affichage
    dictCode = {0: "France",
                1: "Barrage",
                2: "PV",
                3: "Centrale",
                4: "E_ON",
                5: "E_OFF",
                6: "Methaniseur"}

    #Le detecteur
    det = cv.aruco.ArucoDetector()

    # Le detecteur de code Aruco
    dico = dictImg


    for k in dico: # Pour chaque image

        # Liste des IDs contenus dans chaque zone
        

        print("\n################\n")

        img = cv.imread(dico[k]) # Lecture de img
        print(dico[k][10:])
        print("")

        locateAruco(img, det, dictZone)

        print("Carte utilisee : " + dictCode[dictZone["Carte"]] + "\n")
        print("Elements detectes :")
        for k in dictZone:
            print("")
            if dictZone[k] != 0:
                c = Counter(dictZone[k])
                print(k + " : ")
                for i in c:
                        print("  - {} ".format(c[i]) + dictCode[i])
    

    print("")

    output = {"Carte" : dictCode[dictZone["Carte"]]}
    for k in dictZone:
        if k != "Carte":
            output[k] = []
            c = Counter(dictZone[k])
            for i in c:
                output[k].append({"nom":dictCode[i], "nombre":c[i]})


    with open("data_output.json", "w") as f:
        json.dump(output, f)