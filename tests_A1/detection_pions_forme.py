import numpy as np
from collections import Counter
import cv2 as cv
import sys
from math import sqrt
import json


# Affichage de fenetre
def display(title, img):
    cv.imshow(title, img)
    cv.waitKey(0) # Attente d'appui sur une touche
    cv.destroyAllWindows()


# Localise la region
def locateMap(box, pion, result, forme):
    locImg = cv.imread("img/proto-regions.png")
    hsv = cv.cvtColor(locImg, cv.COLOR_BGR2HSV)
    x = box[0][0]
    y = box[0][1]

    # Couleur par region
    regions = {"hdf" : (hsv[100][700] - np.array([2, 20, 20]), hsv[100][700] + np.array([2, 20, 20])),
           "idf" : (hsv[200][700] - np.array([2, 20, 20]), hsv[200][700] + np.array([2, 20, 20])),
           "bre" : (hsv[300][300] - np.array([2, 20, 20]), hsv[300][300] + np.array([2, 20, 20])),
           "pll" : (hsv[400][400] - np.array([2, 20, 20]), hsv[400][400] + np.array([2, 20, 20])),
           "cvl" : (hsv[400][700] - np.array([2, 20, 20]), hsv[400][700] + np.array([2, 20, 20])),
           "bfc" : (hsv[400][900] - np.array([2, 20, 20]), hsv[400][900] + np.array([2, 20, 20])),
           "pac" : (hsv[900][900] - np.array([2, 20, 20]), hsv[900][900] + np.array([2, 20, 20])),
           "occ" : (hsv[700][700] - np.array([2, 20, 20]), hsv[700][700] + np.array([2, 20, 20])),
           "naq" : (hsv[500][500] - np.array([2, 20, 20]), hsv[500][500] + np.array([2, 20, 20])),
           "est" : (hsv[200][900] - np.array([2, 20, 20]), hsv[200][900] + np.array([2, 20, 20])),
           "ara" : (hsv[600][900] - np.array([2, 20, 20]), hsv[600][900] + np.array([2, 20, 20])),
           "nor" : (hsv[100][500] - np.array([2, 20, 20]), hsv[100][500] + np.array([2, 20, 20])),
           "cor" : (hsv[900][1100] - np.array([2, 20, 20]), hsv[900][1100] + np.array([2, 20, 20]))}

    
    val = [1, 3, 5]
    valBis = [2, 4, 6]
    
    for reg in regions:
        if (hsv[y][x] >= regions[reg][0]).all() and (hsv[y][x] <= regions[reg][1]).all():
            print("[PION] {} en region {}".format(pion, reg))
            if pion == "centraleNuc":
                result[reg][pion] += valBis[forme]
            else:
                result[reg][pion] += val[forme]


# Recupere le niveau de stock
def locateStock(box, result):
    p0 = box[0]

    p1 = np.array([1205,447])
    p2 = np.array([1225,445])
    p3 = np.array([1245,443])
    p4 = np.array([1264,443])
    p5 = np.array([1286,443])
    p6 = np.array([1307,441])
    p7 = np.array([1326,442])
    p8 = np.array([1344,442])
    p9 = np.array([1365,443])
    p10 = np.array([386,441])

    dist = [np.sqrt(np.sum((p0-p1)**2)),
            np.sqrt(np.sum((p0-p2)**2)),
            np.sqrt(np.sum((p0-p3)**2)),
            np.sqrt(np.sum((p0-p4)**2)),
            np.sqrt(np.sum((p0-p5)**2)),
            np.sqrt(np.sum((p0-p6)**2)),
            np.sqrt(np.sum((p0-p7)**2)),
            np.sqrt(np.sum((p0-p8)**2)),
            np.sqrt(np.sum((p0-p9)**2)),
            np.sqrt(np.sum((p0-p10)**2))]

    # Retourne 1 si le pion est plus proche de la 1ere case, etc.
    print("[STOCK]", np.argmin(dist) + 1)
    result["stock"] = int(np.argmin(dist) + 1)


# Recupere l'annee
def locateTime(box, result):
    p0 = box[0]

    p1 = np.array([1314,873])
    p2 = np.array([1306,810])
    p3 = np.array([1304,745])
    p4 = np.array([1304,688])
    p5 = np.array([1304,636])


    dist = [np.sqrt(np.sum((p0-p1)**2)),
            np.sqrt(np.sum((p0-p2)**2)),
            np.sqrt(np.sum((p0-p3)**2)),
            np.sqrt(np.sum((p0-p4)**2)),
            np.sqrt(np.sum((p0-p5)**2))]

    # Retourne 1 si le pion est plus proche de la 1ere case, etc.
    print("[SCENARIO]", 2030 + np.argmin(dist) * 5)
    result["annee"] = int(2030 + np.argmin(dist) * 5)


# Renvoie vrai si fait partie de la légende
def whichPart(box):
    if (205 <= box[0][0] and box[1][0] < 1190):
        out = "map"

    elif (box[0][0] >= 1190) and (box[2][1] < 100):
        out = "palette"

    elif (box[0][0] >= 1190) and (box[0][1] > 415) and (box[2][1] < 480):
        out = "stock"

    elif (box[0][0] >= 1190) and (box[0][1] > 590):
        out = "time"

    else:
        out = "err"
    
    return out


# Recupere les 4 coins du plateau
def getBoardCorners(img, result):
    # Le detecteur de code Aruco
    det = cv.aruco.ArucoDetector()

    pts, ids, reject = det.detectMarkers(img)
    corners = []

    # On garde les coordonnees des Aruco dont l'id est 0
    for i in range(len(ids)):
        if ids[i][0] == 0:
            corners.append(pts[i][0].astype(int))
            result["carte"] = "france"


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
def detColor(img, result):
    # display("Image d'origine", img)

    # On recupere les coins
    boardCorners = getBoardCorners(img, result)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [1395,5], [1395,995], [5,995]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1400,1000))

    # cv.imwrite("tests_A1/img/ref_triangle.png", img)
    # sys.exit(0)
    

    # On recupere les nouveaux coins
    boardCorners = getBoardCorners(img, result)
    # display("Perspective corrigee", img)

    # Contours du plateau
    cv.polylines(img, np.array([boardCorners]), True, (255,255,255), 2)
    # display("Detection du plateau", img)



    # Etalonnage
    hsv = cv.imread("img/proto-REF.png")
    hsv = cv.cvtColor(hsv, cv.COLOR_BGR2HSV)
    pions = {"centraleNuc" : (hsv[30][1290] - np.array([3, 40, 60]), hsv[30][1290] + np.array([3, 40, 60])),
           "biomasse" : (hsv[30][1210] - np.array([5, 40, 60]), hsv[30][1210] + np.array([5, 40, 60])),
           "eolienneON" : (hsv[60][1290] - np.array([5, 40, 60]), hsv[60][1290] + np.array([5, 40, 60])),
          # "foret" : (hsv[60][1250] - np.array([5, 40, 60]), hsv[60][1250] + np.array([5, 40, 60])),
           "eolienneOFF" : (hsv[60][1210] - np.array([5, 40, 60]), hsv[60][1210] + np.array([5, 40, 60])),
           "panneauPV" : (hsv[30][1250] - np.array([5, 40, 60]), hsv[30][1250] + np.array([5, 40, 60])),
           "centraleTherm" : (hsv[30][1315] - np.array([5, 40, 60]), hsv[30][1315] + np.array([5, 40, 60]))
           }
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    
    # Pour chaque couleur : application de masque + detection de contours
    for p in pions:
        thresh = cv.inRange(hsv, pions[p][0], pions[p][1])
        # display(p+" mask", thresh)

        # Reduction bruit hors contours puis dans contours
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
        # display(p+" close", close)

        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        open = cv.morphologyEx(close, cv.MORPH_OPEN, kernel)
        # display(p+" open", open)

        contours = cv.findContours(open, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contours = contours[0]

        # Pour chaque contour : trouver le rectangle qui matche le mieux puis tous les dessiner
        sketch = img.copy()
        for c in contours:
            peri = cv.arcLength(c, True)
            approx = cv.approxPolyDP(c, 0.04 * peri, True)
            l = len(approx)
            
            if 4 <= l <= 6:
        
                rot_rect = cv.minAreaRect(c)
                box = cv.boxPoints(rot_rect)
                box = np.int0(box)

                boxArea = whichPart(box)

                if boxArea == "map":
                    cv.drawContours(sketch,[approx],0,(0,255,0),2)
                    locateMap(box, p, result, l-4)

                elif boxArea == "stock":
                    cv.drawContours(sketch,[approx],0,(0,255,0),2)
                    locateStock(box, result)

                elif boxArea == "time":
                    cv.drawContours(sketch,[approx],0,(0,255,0),2)
                    locateTime(box, result)


        # display("contours", sketch)


# [Developpement] Cree une image avec perspective corrigee pour travailler dessus
def createRef(img):
    # On recupere les coins
    boardCorners = getBoardCorners(img)

    # Correction de la perspective
    pts1 = np.float32(boardCorners)
    pts2 = np.float32([[5,5], [1395,5], [1395,995], [5,995]])
    M = cv.getPerspectiveTransform(pts1,pts2)
    img = cv.warpPerspective(img,M,(1400,1000))

    cv.imwrite("img/proto-REF.png", img)
    sys.exit(0)


# Fonction principale
def main():

    # Output final
    result = {"carte":"", "annee":0, "stock":0,
                "hdf" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "idf" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "est" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "nor" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "occ" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "pac" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "bre" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "cvl" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "pll" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "naq" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "ara" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "bfc" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0},
                "cor" : {"eolienneON":0 , "eolienneOFF":0 , "panneauPV":0 , "centraleTherm":0 , "centraleNuc":0 , "biomasse":0}}



    # Pour boucler sur toutes les images
    dictImg =  {0: "img/proto-3.jpg"} 



    for k in dictImg: # Pour chaque image

        print("\n################\n")

        img = cv.imread(dictImg[k]) # Lecture de img
        print(dictImg[k])
        print("")

        detColor(img, result)
    
        
    with open("det_output.json", "w") as f:
        json.dump(result, f)


    print("")    


# img = cv.imread("img/proto-2.jpg")
# createRef(img)

main()