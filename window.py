#import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QDesktopWidget, QApplication, QTextEdit, QLabel, QListWidget, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#import modules visuels
import graph_display as graph
import gps_guide as gps

#import des algorithmes
import dijkstra_mono
import dijkstra_bi
import dijkstra_multi
import astar_mono
import astar_bi
import astar_multi

import math
import matplotlib.pyplot as plt
import roadworks

WINDOW_ICON = "ICON/icon.png"

BUTTONS_SETTINGS_NAME = ['Reset', 'Help', 'Settings']
BUTTONS_SETTINGS_FUNCTION = ['reset', 'help_window.show', 'settings']
SETTINGS_BUTTONS_ICON = ['ICON/reset.png', 'ICON/help.png', 'ICON/setting.png']
VALID_ICON = "ICON/valid.png"
CHOSE_MAP_ICON = 'ICON/ChooseMap.png'

BUTTON_DIALOG_NAME = 'Click here to choose on the map'
BUTTON_DIALOG_FUNCTION = 'fire_choice'

BUTTONS_ALGO_NAME = ['Monodirectional Dijkstra', 'Bidirectional Dijkstra', 'Multidirectional Dijkstra', 'Monodirectional A*', 'Bidirectional A*', 'Multidirectional A*']
BUTTONS_ALGO_FUNCTION = ['dijk_mono', 'dijk_bi', 'dijk_multi', 'a_star_mono', 'a_star_bi', 'a_star_multi']

BUTTONS_SET_STA_NAME = ['Add station', 'Remove station']
BUTTONS_SET_STA_FUNCTION = ['add_station', 'remove_station']

BUTTONS_SET_ROAD_NAME = ['Add roadwork', 'Remove roadwork']
BUTTONS_SET_ROAD_FUNCTION = ['add_roadwork', 'remove_roadwork']

class MainWindow(QMainWindow):

    def __init__(self, fname, names, coords):
        super(MainWindow, self).__init__()
        self.station_names = names
        self.station_names_init = self.station_names.copy()
        self.station_coords = coords
        self.setWindowIcon(QtGui.QIcon(WINDOW_ICON))
        self._main = QWidget()
        self.setCentralWidget(self._main)
        self.initUI()  # initialisation fenêtre principale
        self.initGraph(fname) #initialisation du graphe
        self.initPos() #initisaliation de la source et de la destination à une valeur par défaut
        self.initRoadworks()  # initialisation de l'attribut travaux
        self.initColorDict() #initialisation des dictionnaires pour la coloration du graphe
        self.updateGraph() #mise à jour du graphe

    def initUI(self):
        """
        initialise la fenêtre globale et son interface
        """
        self.grid = QGridLayout(self._main)  # grille de layout pour le widget central
        self._main.setLayout(self.grid)  # définition du layout du widget central

        self.setGeometry(QDesktopWidget().availableGeometry()) #mise en plein écran de la fenêtre
        self.setWindowTitle('Map - Fire in Manhattan')

        #création de la figure matplotlib pour accueillir le graph
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        self.grid.addWidget(self.canvas, 0, 2, 9, 9) #ajout de la figure matplotlib au layout
        self.addToolBar(NavigationToolbar(self.canvas, self)) #ajout de la toolbar lié à la figure matplotlib
        self.show()

        self.createHelp() #crée le widget "help"
        self.createSettingsButtons(BUTTONS_SETTINGS_NAME, BUTTONS_SETTINGS_FUNCTION, SETTINGS_BUTTONS_ICON) #création des boutons de réglages (tout en haut)
        self.createButtonsAlgo(BUTTONS_ALGO_NAME, BUTTONS_ALGO_FUNCTION)  # création des boutons pour le choix algo
        self.createBoxGps(BUTTON_DIALOG_NAME, BUTTON_DIALOG_FUNCTION)  # création du formulaire pour le choix GPS
        self.createStationForm(self.station_names_init)
        self.createPathBox()  # crée la boite d'affichage du chemin
        self.createStationBox() #crée la boite d'affichage de la caserne
        self.createSettingsUI() #crée les boites pour les réglages de l'application

    def initGraph(self, fname):
        """
        initialise le graphe
        """
        parser = graph.GraphDisplayML()  # renomage commande
        self.graphe = parser.parse(fname)  # création du graph

    def initPos(self):
        """
        initialise les positions sources et destination par défaut
        """
        self.dest = []
        for i,(x,y) in enumerate(self.station_coords):
            node = self.closest_node(x, y)
            node.station = self.station_names_init[i]
            self.dest.append(node)
        self.currentDest = self.dest[0]
        self.station_label.setText("The current station is :\n" + self.currentDest.station)
        self.src = self.graphe.nodes()[0]

    def initColorDict(self):
        """
        initialise le dictionnaire des liaisons, ainsi que leur couleur, avec comme clé, les noeuds de la liaison
        initialise le dictionnaire des noeuds et leur couleur
        """
        self.graphe.node_dict = {}
        self.graphe.edge_dict = {}
        for n in self.graphe.nodes():
            n.color = graph.DEFAULT_NODE_COLOR
            self.graphe.node_dict[n.id] = n
        self.src.color = graph.SRC_COLOR
        for elt in self.dest:
            elt.color = graph.DEST_COLOR
        self.currentDest.color = graph.CHOSEN_DEST_COLOR
        for e in self.graphe.edges():
            e.color = graph.DEFAULT_EDGE_COLOR
            self.graphe.edge_dict[(e.node1, e.node2)] = e
            if e.roadworks:
                e.color = graph.EDGE_ROADWORKS_COLOR

    def initRoadworks(self):
        roadworks.add_attribut_roadworks(self.graphe)

    def createButtons(self, names, functions, layout):
        buttons = []
        for i, name in enumerate(names):
            button = QPushButton(name)
            button.clicked.connect(eval("self." + functions[i]))
            buttons.append(button)
            layout.addWidget(button)
        return buttons

    def createButtonsAlgo(self, buttons_algo_name, buttons_algo_function):
        """
        création des bouttons pour le choix algo
        """
        self.button_algo_box = QGroupBox("Algorithm choice", self._main)
        layout = QVBoxLayout()
        self.button_algo_box.setLayout(layout)
        self.createButtons(buttons_algo_name, buttons_algo_function, layout)
        self.grid.addWidget(self.button_algo_box, 2, 0, 3, 2)

    def createSettingsButtons(self, button_names, button_functions, button_icon):
        layout = QHBoxLayout()
        buttons = self.createButtons(button_names, button_functions, layout)
        self.settingsButton = buttons[-1]
        for i, b in enumerate(buttons[:2]):
            b.setIcon(QtGui.QIcon(button_icon[i]))
        self.settingsButton.setIcon(QtGui.QIcon(button_icon[-1]))
        self.grid.addLayout(layout, 0, 0, 1, 2)

    def createSettingsUI(self):
        self.settingsStation = QGroupBox("Stations settings",self._main)
        layout = QHBoxLayout()
        self.createButtons(BUTTONS_SET_STA_NAME, BUTTONS_SET_STA_FUNCTION, layout)
        layout2 = QVBoxLayout()
        self.settings_station_edit = QLineEdit()
        self.settings_station_label = QLabel()
        self.settings_station_label.setAlignment(Qt.AlignCenter)
        layout2.addWidget(self.settings_station_label)
        layout2.addLayout(layout)
        layout2.addWidget(self.settings_station_edit)
        self.settingsStation.setLayout(layout2)
        self.grid.addWidget(self.settingsStation, 1, 0, 1, 2)
        self.settingsStation.hide()

        self.settingsRoadworks = QGroupBox("Roadworks settings",self._main)
        layout = QVBoxLayout()
        layout2 = QHBoxLayout()
        self.settings_road_label = QLabel()
        self.settings_road_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.settings_road_label)
        self.createButtons(BUTTONS_SET_ROAD_NAME, BUTTONS_SET_ROAD_FUNCTION, layout2)
        layout.addLayout(layout2)
        self.settingsRoadworks.setLayout(layout)
        self.grid.addWidget(self.settingsRoadworks, 2, 0, 1, 2)
        self.settingsRoadworks.hide()

    def createBoxGps(self, button_name, button_function):
        """
        creation de la boite de choix gps
        """
        self.gps_box = QGroupBox("Fire choice", self._main)
        layout = QHBoxLayout()
        button = QPushButton(button_name)
        button.setObjectName(button_name)
        button.setIcon(QtGui.QIcon(CHOSE_MAP_ICON))
        layout.addWidget(button)
        button.clicked.connect(eval("self." + button_function))
        self.gps_box.setLayout(layout)
        self.grid.addWidget(self.gps_box, 1, 0, 1, 2)

    def createPathBox(self):
        """
        création de la boite affichage info chemin et caserne
        """
        self.path_box = QGroupBox("Algorithm result", self._main)
        layout = QVBoxLayout()
        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.path_label)
        button = QPushButton("GPS Guidance")
        button.clicked.connect(self.guidage_gps)
        layout.addWidget(button)
        self.path_box.setLayout(layout)
        self.grid.addWidget(self.path_box, 6, 0, 1, 2)
        self.path_box.hide()

    def createStationBox(self):
        self.station_box = QGroupBox("Fire station", self._main)
        layout = QVBoxLayout()
        self.station_label = QLabel()
        self.station_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.station_label)
        self.station_box.setLayout(layout)
        self.grid.addWidget(self.station_box, 5, 0, 1, 2)

    def createStationForm(self, names):
        layout = QVBoxLayout()
        self.station_list_box = QGroupBox("Choice of station", self._main)
        self.listView = QListWidget(self._main)
        layout.addWidget(self.listView)
        self.station_list_box.setLayout(layout)
        self.listView.addItems(names)
        self.grid.addWidget(self.station_list_box, 7, 0, 1, 2)
        self.listView.clicked.connect(self.select_station)
        self.station_list_box.hide()

    def createHelp(self):
        self.help_window = QWidget()
        self.help_window.setWindowTitle("Help")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setFontPointSize(14)
        text.setText(open("DATA/help.txt","r").read())
        layout = QHBoxLayout()
        layout.addWidget(text)
        self.help_window.setLayout(layout)
        self.help_window.setMinimumSize(600, 600)

    def select_station(self):
        self.resetGraph()
        index = self.listView.currentRow()
        self.currentDest.color = graph.DEST_COLOR
        self.currentDest = self.dest[index]
        self.currentDest.color = graph.CHOSEN_DEST_COLOR
        self.updateGraph()
        algorithm(self, self.algo)

    def fire_choice(self):
        self.resetGraph()
        self.resetUI()
        self.cid = self.canvas.mpl_connect('button_press_event', self.valid_gps_fire)

    def valid_gps_fire(self, event):
        """
        calcul la source la plus proche en fonction de l'endroit où la souris a cliqué
        """
        x, y = event.xdata, event.ydata
        self.src.color = graph.DEFAULT_NODE_COLOR  # le noeud précedent devient un noeud ordinaire
        self.src = self.closest_node(x, y)
        self.src.color = graph.SRC_COLOR  # mise à jour couleur noeud
        self.updateGraph()  # mise à jour du graph
        self.canvas.mpl_disconnect(self.cid) #déconnection des mouse press event

    def closest_node(self, x, y, bool=False):
        """
        trouve le noeud le plus proche des coordonnées (x,y)
        """
        def distance(lat, long, noeud):
            x = float(noeud['d4'])
            y = float(noeud['d3'])
            return math.sqrt((lat-x)**2+(long-y)**2)
        if not bool:
            closestN = self.graphe.nodes()[0]
            minDist = distance(x, y, closestN)
            for n in self.graphe.nodes()[1:]:  # premier élément déjà parcouru
                dist = distance(x, y, n)
                if min(dist, minDist) == dist:
                    minDist = dist
                    closestN = n
            return closestN
        else:
            closestN = self.dest[0]
            minDist = distance(x, y, closestN)
            for n in self.dest[1:]:  # premier élément déjà parcouru
                dist = distance(x, y, n)
                if min(dist, minDist) == dist:
                    minDist = dist
                    closestN = n
            return closestN

    def settings(self):
        self.resetGraph()
        self.settingsStation.show()
        self.settingsRoadworks.show()
        self.settingsButton.setText("Valid")
        self.settingsButton.clicked.disconnect(self.settings)
        self.settingsButton.clicked.connect(self.valid_settings)
        self.settingsButton.setIcon(QtGui.QIcon(VALID_ICON))
        self.settings_station_edit.setText("")
        self.settings_station_label.setText("")
        self.settings_road_label.setText("")
        self.path_box.hide()
        self.button_algo_box.hide()
        self.station_box.hide()
        self.station_list_box.hide()
        self.gps_box.hide()

    def resetUI(self):
        self.settingsStation.hide()
        self.settingsRoadworks.hide()
        self.settingsButton.setText("Settings")
        self.settingsButton.setIcon(QtGui.QIcon(SETTINGS_BUTTONS_ICON[-1]))
        self.button_algo_box.show()
        self.station_box.show()
        self.station_list_box.hide()
        self.gps_box.show()

    def valid_settings(self):
        self.resetUI()
        self.resetGraph()
        self.settingsButton.clicked.disconnect(self.valid_settings)
        self.settingsButton.clicked.connect(self.settings)

    def add_station(self):
        def newStation(event):
            x, y = event.xdata, event.ydata
            name = self.settings_station_edit.text()
            if name != "":
                station = self.closest_node(x, y)
                station.station = name
                station.color = graph.DEST_COLOR
                self.dest.append(station)
                self.station_names.append(name)
                self.listView.addItem(name)
                self.canvas.mpl_disconnect(cid)
                self.settings_station_label.setText("Done")
                self.updateGraph()
            else:
                self.settings_station_label.setText("You have to name your station to create it")
        self.settings_station_label.setText("Please enter a name of the station before clicking")
        cid = self.canvas.mpl_connect('button_press_event', newStation)

    def remove_station(self):
        def delStation(event):
            x, y = event.xdata, event.ydata
            station = self.closest_node(x,y,True)
            station.color = graph.DEFAULT_NODE_COLOR
            station.station = None
            i = self.dest.index(station)
            self.dest.pop(i)
            self.station_names.pop(i)
            self.listView.takeItem(i)
            if self.currentDest == station:
                self.currentDest = self.dest[0]
            self.canvas.mpl_disconnect(cid)
            self.settings_station_label.setText("Done")
            self.updateGraph()

        self.settings_station_label.setText("Please click on the station to remove it")
        cid = self.canvas.mpl_connect('button_press_event', delStation)

    def add_roadwork(self):
        nodes = []
        self.settings_road_label.setText("Click on the first crossroad")
        def click_add(event):
            x, y = event.xdata, event.ydata
            n = self.closest_node(x, y)
            nodes.append(n)
            self.settings_road_label.setText("Click on the second crossroad")
            length = len(nodes)
            if length == 2:
                roadworks.add_roadworks(self.graphe, nodes[0], nodes[1])
                self.updateGraph()
                self.canvas.mpl_disconnect(cid)
                self.settings_road_label.setText("Roadwork has been added")
            elif length > 2:
                self.settings_road_label.setText("Something went wrong\nPlease try again")
                self.canvas.mpl_disconnect(cid)
        cid = self.canvas.mpl_connect('button_press_event', click_add)

    def remove_roadwork(self):
        nodes = []
        self.settings_road_label.setText("Click on the first crossroad")
        def click(event):
            x, y = event.xdata, event.ydata
            n = self.closest_node(x, y)
            nodes.append(n)
            self.settings_road_label.setText("Click on the second crossroad")
            length = len(nodes)
            if length == 2:
                roadworks.remove_roadworks(self.graphe, nodes[0], nodes[1])
                self.updateGraph()
                self.canvas.mpl_disconnect(cid)
                self.settings_road_label.setText("Roadwork has been deleted")
            elif length > 2:
                self.settings_road_label.setText("Something went wrong\nPlease try again")
                self.canvas.mpl_disconnect(cid)

        cid = self.canvas.mpl_connect('button_press_event', click)

    def updateGraph(self):
        """
        mise à jour du graphe
        """
        self.figure.clf()  # effaçage de la figure
        self.graphe.show(graph.SHOW_LABEL)  # création affichage du graph
        self.figure.canvas.draw()  # affichage du graph dans Qt

    def resetGraph(self):
        """
        remet à zéro le graph sans changer la source si elle n'était plus à sa valeur par défaut, ni les travaux
        """
        self.initColorDict()
        self.updateGraph()
        self.path_box.hide()
        self.station_label.setText("The current station is :\n" + self.currentDest.station)

    def resetList(self):
        """
        remet à zéro les listes des noms
        """
        def resetStation(self):
            self.listView.clear()
            self.listView.addItems(self.station_names_init)
        resetStation(self)

    def reset(self):
        """
        remet à zéro toute la fenêtre et le graph aux valeurs par défaut
        """
        self.initRoadworks()
        self.initPos()
        self.resetList()
        self.resetGraph()
        self.resetUI()

    def dijk_mono(self):
        algorithm_multi(self, dijkstra_mono.dijkstra)

    def dijk_bi(self):
        self.resetGraph()
        self.algo = dijkstra_bi.dijkstra
        self.station_list_box.show()

    def dijk_multi(self):
        algorithm_multi(self, dijkstra_multi.dijkstra)

    def a_star_mono(self):
        self.resetGraph()
        self.algo = astar_mono.astar
        self.station_list_box.show()

    def a_star_bi(self):
        self.resetGraph()
        self.algo = astar_bi.astar
        self.station_list_box.show()

    def a_star_multi(self):
        algorithm_multi(self, astar_multi.astar)

    def afficheDist(self, dist):
        """
        affiche la distance dans la boîte prévue
        """
        dist_str = gps.distRound(dist)
        self.path_label.setText("The shortest distance is " + dist_str)
        self.path_box.show()

    def guidage_gps(self):
        """
        affiche la sous-fenêtre pour les indications de guidage gps
        """
        self.subwindow = gps.Gps_Guide(self.graphe, self.path, self.distPath)
        self.subwindow.show()

def algorithm(window, algo):
    window.resetGraph()
    (window.distPath, window.path) = algo(window.graphe, window.src, window.currentDest)
    graph.color_path(window.graphe, window.path, window.src, window.currentDest, window.dest)
    window.updateGraph()
    window.station_label.setText("The current station is :\n" + window.currentDest.station)
    window.afficheDist(window.distPath)

def algorithm_multi(window, algo):
    window.resetGraph()
    window.station_list_box.hide()
    (window.distPath, window.path, caserne) = algo(window.graphe, window.src, window.dest)
    graph.color_path(window.graphe, window.path, window.src, caserne, window.dest)
    window.updateGraph()
    window.afficheDist(window.distPath)
    window.station_label.setText("The closest station is :\n" + caserne.station)

if __name__ == '__main__':
    FIRE_STATIONS_COORD = [(-73.9709356, 40.7568252), (-73.9803139, 40.7667635), (-73.9925139, 40.7269785),(-73.9965901, 40.7607144), (-73.9819548, 40.754986), (-73.99590301513672, 40.75651168823242),(-73.9903493, 40.7531329), (-73.99292755126953, 40.749488830566406),(-73.9788719, 40.7416903), (-73.9909999, 40.7379575), (-74.0003435, 40.7343848),(-73.9894278, 40.7331362), (-73.9925139, 40.7269785), (-73.99652, 40.722966),(-74.006613, 40.7195531), (-73.9928353, 40.7153986), (-73.98375701904297, 40.71654510498047),(-74.00617218017578, 40.7153434753418), (-74.0054049, 40.7099474), (-74.0125962, 40.7098024),(-74.0075414, 40.7036231), (-73.9775390625, 40.781097412109375), (-73.9745417, 40.7847243),(-73.9468848, 40.7888935), (-73.94737243652344, 40.79893112182617), (-73.9365227, 40.803304),(-73.942466, 40.8133131)]
    FIRE_STATIONS_NAME = ["FDNY Engine 8/Ladder 2/Battalion 8", "FDNY Engine 23", "FDNY Engine 33/Ladder 9","FDNY Rescue 1", "FDNY Engine 65", "FDNY Engine 34/Ladder 21", "FDNY Engine 26", "FDNY Engine 1/Ladder 24", "FDNY Engine 16/Ladder 7", "FDNY Engine 14", "FDNY Squad 18","FDNY Ladder 3/Battalion 6", "FDNY Engine 33/Ladder 9", "FDNY Ladder 20/Division 1","FDNY Ladder 8", "FDNY Engine 9/Ladder 6", "FDNY Engine 15/Ladder 18/Battalion 4","FDNY Engine 7/Ladder 1/Battalion 1", "FDNY Ten House", "NYC Fire Department Engine 4","FDNY Ladder 25/Division 3/Collapse Rescue 1", "FDNY Engine 74","FDNY Engine 53/Ladder 43/Rac. 1", "FDNY Engine 91", "FDNY Engine 58/Ladder 26","FDNY Engine 35/Ladder 14/Battalion 12", "FDNY Engine 59/Ladder 30"]
    import sys
    FILE = 'DATA/manhattan.graphml'
    app = QApplication(sys.argv)
    window = MainWindow(FILE, FIRE_STATIONS_NAME, FIRE_STATIONS_COORD)
    window.show()
    sys.exit(app.exec_())