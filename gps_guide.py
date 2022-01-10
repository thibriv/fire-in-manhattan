from PyQt5.QtWidgets import QMainWindow, QGridLayout, QVBoxLayout, QWidget, QTextEdit, QGroupBox, QPushButton
from PyQt5.QtTextToSpeech import QTextToSpeech
from PyQt5.QtCore import QLocale

import numpy as np
import math

TOOLBAR_BUTTONS = ['Previous instruction', 'Replay', 'Next instruction']
TOOLBAR_FUNCTIONS = ['previous_say', 'replay', 'next_say']
LANGUAGE_NUMBER = 31 #english

class Gps_Guide(QMainWindow):
    def __init__(self, graph, path, dist):
        super(Gps_Guide,self).__init__()
        self.setWindowTitle("GPS Guidance")
        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.layout = QVBoxLayout(self._main)
        self.display = QTextEdit()
        self.display.setReadOnly(True)
        self.display.setFontPointSize(14)
        self.sound = QTextToSpeech()
        locale = QLocale(LANGUAGE_NUMBER)
        self.sound.setLocale(locale)
        self.toolbar = self.initToolbar(TOOLBAR_BUTTONS, TOOLBAR_FUNCTIONS)
        self.layout.addWidget(self.display)
        self.layout.addWidget(self.toolbar)
        self._main.setLayout(self.layout)
        self.setMinimumSize(500, 500)
        self.guidance(graph, path, dist)

    def initToolbar(self, buttons_name, functions_name):
        box = QGroupBox("Vocal guidance", self._main)
        layout = QGridLayout()
        for i,b in enumerate(buttons_name):
            button = QPushButton(b,box)
            layout.addWidget(button, 0, i)
            button.clicked.connect(eval("self." + functions_name[i]))
        box.setLayout(layout)
        return box

    def guidance(self, graph, path, distTotal):
        """
        écrit un fichier txt dans GPS/gps.txt avec les indications de guidage GPS
        affiche les indications dans la sous-fenêtre qt
        initialise le compteur d'instruction pour la synthèse vocale
        """
        node_dict = graph.node_dict
        nodes = []
        for n_id in path: #création liste des noeuds du chemin
            n = node_dict[n_id]
            nodes.append(n)
        nodes.reverse()
        l_nodes = len(nodes)

        with open("DATA/gps.txt", "w") as f: #ouverture/création du fichier gps.txt
            i = 1
            j = 0 #indicateur de première boucle
            while i < l_nodes:  # parcourt de la liste edges pour écrire indication dans le fichier
                e = get_edge(graph, nodes[i - 1], nodes[i])
                street = e['d8']
                dist = float(e['d9'])
                i += 1
                k = i - 1
                while i < l_nodes:  # tant que les rues "suivantes" ont le même nom
                    e = get_edge(graph, nodes[i - 1], nodes[i])
                    if street == e['d8']:
                        dist += float(e['d9'])
                        i += 1
                    else:
                        break
                dist_str = distRound(dist)
                if j == 0: #première rue visitée
                    f.write("Take " + street + " for " + dist_str + "\n\n")
                else :
                    n1, n2, n3 = nodes[k - 2], nodes[k - 1], nodes[k]
                    direction = orientation(n1, n2, n3)
                    f.write(direction + street + " for " + dist_str + "\n\n")
                j += 1
            distTotal_str = distRound(distTotal)
            f.write("\nYou have just arrived after " + distTotal_str)
        with open("DATA/gps.txt","r") as f: #lecture du fichier pour synthèse vocale
            self.instructions = []
            for line in f:
                if line != "\n":
                    self.instructions.append(line)
        self.display.setText(open("DATA/gps.txt","r").read()) #affichage des instructions dans la sous-fenêtre
        self.lineToSay = 0 #indice du numéro de l'instruction à lire

    def previous_say(self):
        """demande la lecture de l'instruction précédente"""
        if self.lineToSay <= 1 :
            self.sound.say("No previous instruction to say")
        else:
            self.lineToSay -= 2
            self.play(self.lineToSay)
            self.lineToSay += 1

    def replay(self):
        """rejoue l'instruction"""
        if self.lineToSay != 0:
            self.lineToSay -=1
            self.play(self.lineToSay)
            self.lineToSay +=1
        else:
            self.sound.say("No instruction to replay")

    def next_say(self):
        """demande la lecture de la prochaine instruction"""
        if self.lineToSay < len(self.instructions):
            self.play(self.lineToSay)
            self.lineToSay += 1
        else:
            self.sound.say("No more instruction to say")

    def play(self, line):
        """Lit la ligne d'instruction d'indice line"""
        instruction = self.instructions[line]
        self.sound.say(instruction)

def get_edge(graph, n1, n2):
    try:
        e = graph.edge_dict[(n1,n2)]
    except KeyError:
        e = graph.edge_dict[(n2,n1)]
    street_name(e)
    return e

def distRound(dist):
    """
    arrondi la distance dist puis la transforme en chaine de caractère avec unité et typographie française
    """
    if dist // 1000 != 0:  # distance de l'ordre du kilomètre
        dist = round(dist, 0)
        km = int(dist // 1000)
        rest = dist % 1000
        m = rest * 1000
        dist_str = str(km) + "," + str(m)[:3] + " km"
        return dist_str
    else:  # distance de l'ordre du mètre
        m = round(dist, 0)
        m = int(m)
        dist_str = str(m) + " m"
        return dist_str

def orientation(n1,n2,n3):
    """
    :param n1: noeud pré virage
    :param n2: noeud du virage
    :param n3: noeud destination
    :return: renvoie si on doit prendre à gauche ou à droite pour changer de rue avec une distinction entre tourner (>=45°) et diriger (<45°)
    """

    def vectorisation(n1, n2):
        x1,y1 = n1['d4'],n1['d3']
        x2, y2 = n2['d4'], n2['d3']
        x = float(x2)-float(x1)
        y = float(y2)-float(y1)
        vect = [x, y]
        return vect

    v_dir = vectorisation(n1, n2) #direction de la route
    v_dest = vectorisation(n1, n3) #vecteur entre noeud pré-origine et destination
    v_suite = vectorisation(n2, n3) #vecteur de la suite du chemin après le virage en n2
    angle = math.acos(np.vdot(v_dir, v_suite)/(np.linalg.norm(v_dir)*(np.linalg.norm(v_suite))))
    prod_vec=np.cross(v_dir,v_dest)
    if prod_vec>0: #vers la gauche
        if angle >= math.pi/4:
            return "Turn left on "
        else :
            return "Go to the left on "
    elif angle >= math.pi / 4:
        return "Turn right on "
    else :
        return "Go to the right on "

def street_name(e):
    """
    vérifie/ajoute si l'attribut d8 (nom de rue) est présent sur e
    """
    try:  # test si l'attribut du nom de rue existe
        e['d8']
    except KeyError:  # ajout de l'attribut à une valeur par défaut si l'attribut n'existe pas
        e['d8'] = "road without name"