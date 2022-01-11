from pygraphml import Graph as pGraph
from pygraphml import GraphMLParser
from xml.dom import minidom
import numpy as np
import networkx as nx
import gps_guide as gps

EDGE_WIDTH = 0.5
EDGE_PATH_WIDTH = 1
NODE_SIZE = 10
SPECIAL_NODE_SIZE = 60
PATH_NODE_SIZE = 40
NODE_PATH_COLOR = (1,1,0) #yellow
EDGE_PATH_COLOR = (0,128/255,0) #green
EDGE_ROADWORKS_COLOR = (1,0,0) #red
COLOR_NODE_PAR = [(236/255,12/255,34/255),(228/255,14/255,37/255),(219/255,15/255,39/255),(211/255,17/255,42/255),(202/255,18/255,44/255),(194/255,20/255,47/255),(185/255,22/255,50/255),(177/255,23/255,52/255),(169/255,25/255,55/255),(160/255,27/255,58/255),(152/255,28/255,60/255),(143/255,30/255,63/255),(135/255,31/255,65/255),(127/255,33/255,68/255),(118/255,35/255,71/255),(110/255,36/255,73/255),(101/255,38/255,76/255),(93/255,39/255,78/255),(84/255,41/255,81/255),(76/255,43/255,84/255),(68/255,44/255,86/255),(59/255,46/255,89/255),(51/255,48/255,92/255),(42/255,49/255,94/255),(34/255,51/255,97/255),(25/255,52/255,99/255),(17/255,54/255,102/255)]
SRC_COLOR = (1,0,0) #red
DEST_COLOR = (0,208/255,208/255) #cyan
CHOSEN_DEST_COLOR = (100/255,200/255,0) #lime
DEFAULT_NODE_COLOR = (125/255, 125/255, 125/255)#grey
DEFAULT_EDGE_COLOR = (0,0,0)

SHOW_LABEL = False

class Graph(pGraph):
    def show(self,showlabel=True):
        """
        Redéfinition de la méthode show de la classe Graph pour l'incrustation dans la fenêtre Qt
        """
        G = nx.Graph()
        G = G.to_undirected()
        self.pos_dict = {}
        special_pos = {}
        nodes_color = []
        edges_color = []
        edgeslist = []
        nodeslist = []
        nodespath = []
        edgespath = []
        special_nodes = []
        color_special_nodes = []
        for n in self.nodes():
            n_label = n.id
            G.add_node(n_label)
            self.pos_dict[n_label] = np.array([float(n['d4']), float(n['d3'])])  # creation of the positions of the points
            if n.color == NODE_PATH_COLOR :
                nodespath.append(n_label)
            elif n.color in [SRC_COLOR, CHOSEN_DEST_COLOR]:
                special_nodes.append(n)
                color_special_nodes.append(n.color)
                special_pos[n]=np.array([float(n['d4']),float(n['d3'])])
            else:
                nodes_color.append(n.color)
                nodeslist.append(n_label)
        for e in self.edges():
            n1_label = e.node1.id
            n2_label = e.node2.id
            G.add_edge(n1_label, n2_label)
            if e.color == DEFAULT_EDGE_COLOR or e.color == EDGE_ROADWORKS_COLOR:
                edgeslist.append((n1_label, n2_label))
                edges_color.append(e.color)
            else :
                edgespath.append((n1_label, n2_label))
        nx.draw(G, pos = self.pos_dict, node_color = nodes_color, edge_color = edges_color, width = EDGE_WIDTH, nodelist = nodeslist, edgelist = edgeslist, node_size = NODE_SIZE, with_labels = showlabel)
        nx.draw(G, pos = self.pos_dict, node_color = NODE_PATH_COLOR, edge_color= EDGE_PATH_COLOR, width = EDGE_PATH_WIDTH, nodelist = nodespath, edgelist = edgespath, node_size = PATH_NODE_SIZE, with_labels=showlabel)
        nx.draw_networkx_nodes(G, pos = special_pos, node_color = color_special_nodes, nodelist = special_nodes, node_size = SPECIAL_NODE_SIZE)

class GraphDisplayML(GraphMLParser):
    def parse(self, fname):
        """
        redefinition of the methode parse from the GraphMLParser class for the Qt use
        """

        g = None
        with open( fname, 'r') as f:
            dom = minidom.parse(f)
            root = dom.getElementsByTagName("graphml")[0]
            graph = root.getElementsByTagName("graph")[0]
            name = graph.getAttribute('id')

            g = Graph(name)

            # # Get attributes
            # attributes = []
            # for attr in root.getElementsByTagName("key"):
            #     attributes.append(attr)

            # Get nodes
            for node in graph.getElementsByTagName("node"):
                n = g.add_node(id=node.getAttribute('id'))

                for attr in node.getElementsByTagName("data"):
                    if attr.firstChild:
                        n[attr.getAttribute("key")] = attr.firstChild.data
                    else:
                        n[attr.getAttribute("key")] = ""

            # Get edges
            for edge in graph.getElementsByTagName("edge"):
                source = edge.getAttribute('source')
                dest = edge.getAttribute('target')

                # source/target attributes refer to IDs: http://graphml.graphdrawing.org/xmlns/1.1/graphml-structure.xsd
                e = g.add_edge_by_id(source, dest)

                for attr in edge.getElementsByTagName("data"):
                    if attr.firstChild:
                        e[attr.getAttribute("key")] = attr.firstChild.data
                    else:
                        e[attr.getAttribute("key")] = ""

        return g

def color_path(graph, path, src, dest, listdest):
    for i in range(len(path)-1):
       node1 = graph.node_dict[path[i]]
       node1.color = NODE_PATH_COLOR
       node2 = graph.node_dict[path[i+1]]
       node2.color = NODE_PATH_COLOR
       edge = gps.get_edge(graph, node1, node2)
       edge.color = EDGE_PATH_COLOR
    for elt in listdest:
        elt.color = DEST_COLOR
    src.color = SRC_COLOR
    dest.color = CHOSEN_DEST_COLOR