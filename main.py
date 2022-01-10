from PyQt5.QtWidgets import QApplication
import window

GRAPH_FILE = "DATA/manhattan.graphml"
COORDS_FILE = "DATA/manhattan_coords.txt"

def from_coords_file(fname):
    """
    lit les coordonées des stations de pompiers et leur nom dans un fichier txt selon le schéma de ligne suivant : name;x;y
    """
    names = []
    coords = []
    with open(fname, "r") as f:
        for line in f:
            [name, x, y] = line.split(";")
            x, y = float(x), float(y)
            names.append(name)
            coords.append((x,y))
    return names, coords


if __name__=="__main__":
    import sys
    names, coords = from_coords_file(COORDS_FILE)
    app = QApplication(sys.argv)
    mainwindow = window.MainWindow(GRAPH_FILE, names, coords)
    mainwindow.show()
    sys.exit(app.exec_())