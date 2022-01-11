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
        for n_id in path: #creation of the list of the nodes from the path
            n = node_dict[n_id]
            nodes.append(n)
        nodes.reverse()
        l_nodes = len(nodes)

        with open("DATA/gps.txt", "w") as f: #opens/creates the file gps.txt
            i = 1
            j = 0 #indicates the first loop
            while i < l_nodes:  # scan the edges list to write the orders in the file
                e = get_edge(graph, nodes[i - 1], nodes[i])
                street = e['d8']
                dist = float(e['d9'])
                i += 1
                k = i - 1
                while i < l_nodes:  # while the "following" streets have the same name
                    e = get_edge(graph, nodes[i - 1], nodes[i])
                    if street == e['d8']:
                        dist += float(e['d9'])
                        i += 1
                    else:
                        break
                dist_str = distRound(dist)
                if j == 0: #first visited street
                    f.write("Take " + street + " for " + dist_str + "\n\n")
                else :
                    n1, n2, n3 = nodes[k - 2], nodes[k - 1], nodes[k]
                    direction = orientation(n1, n2, n3)
                    f.write(direction + street + " for " + dist_str + "\n\n")
                j += 1
            distTotal_str = distRound(distTotal)
            f.write("\nYou have just arrived after " + distTotal_str)
        with open("DATA/gps.txt","r") as f: #reading of the file for vocal synthesis
            self.instructions = []
            for line in f:
                if line != "\n":
                    self.instructions.append(line)
        self.display.setText(open("DATA/gps.txt","r").read()) #displays the orders in the sub-window
        self.lineToSay = 0 #index of the order to pronounce

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
    if dist // 1000 != 0:  # distance in kilometers
        dist = round(dist, 0)
        km = int(dist // 1000)
        rest = dist % 1000
        m = rest * 1000
        dist_str = str(km) + "," + str(m)[:3] + " km"
        return dist_str
    else:  # distance in meters
        m = round(dist, 0)
        m = int(m)
        dist_str = str(m) + " m"
        return dist_str

def orientation(n1,n2,n3):
    """
    :param n1: before turn node
    :param n2: turn node
    :param n3: after turn node
    :return: returns if you have to got to the left or the right when there is a change of street
    """

    def vectorisation(n1, n2):
        x1,y1 = n1['d4'],n1['d3']
        x2, y2 = n2['d4'], n2['d3']
        x = float(x2)-float(x1)
        y = float(y2)-float(y1)
        vect = [x, y]
        return vect

    v_dir = vectorisation(n1, n2) #direction of the road
    v_dest = vectorisation(n1, n3) #vector between before turn node and destination
    v_suite = vectorisation(n2, n3) #vector of the next path of the turn in n2
    angle = math.acos(np.vdot(v_dir, v_suite)/(np.linalg.norm(v_dir)*(np.linalg.norm(v_suite))))
    prod_vec=np.cross(v_dir,v_dest)
    if prod_vec>0: #to the left
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
    check/add if the d8 attribute (name of street) is present on e
    """
    try:  # if d8 exists
        e['d8']
    except KeyError:  # add it to a default value
        e['d8'] = "road without name"