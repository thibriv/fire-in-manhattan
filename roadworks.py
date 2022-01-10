import graph_display as gr
import gps_guide as gps

def add_attribut_roadworks(graph):
    for elt in graph._edges:
        elt.roadworks = False

def add_roadworks(graph, node1, node2):
    try:
        elt = gps.get_edge(graph, node1, node2)
        elt.roadworks = True
        elt.color = gr.EDGE_ROADWORKS_COLOR
    except KeyError:
        pass

def remove_roadworks(graph, node1,node2):
    try:
        elt=gps.get_edge(graph, node1,node2)
        elt.roadworks = False
        elt.color = gr.DEFAULT_EDGE_COLOR
    except KeyError:
        pass

