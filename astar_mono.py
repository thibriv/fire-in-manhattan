from math import sqrt, inf
import heapdict as hp
import graph_display as g

def astar(graph, src, dest):
    open_list = hp.heapdict()  # heapqueue (nodes to visit)
    for node in graph.nodes():
        node.close = False
        node.h = inf
        node.c = inf
        node.pred = None
    src.h = 0
    src.c = 0
    open_list[src] = src.h
    while open_list:
        u = open_list.popitem()[0]
        u.close = True
        if u == dest:
            return (u.c, path(u))
        for (v, v_weight) in neighbours(graph, u):  # for all neighbours, we get the length of the edge
            current_cost = u.c + v_weight
            v.color = g.COLOR_NODE_PAR[0]
            if not v.close:
                v.c = current_cost
                v.h = distance(v, dest)
                open_list[v] = v.h
                v.pred = u

def neighbours(graph, node):
    n = []
    k = graph.nodes().index(node)
    for elt in graph.nodes()[k].edges():
        oneway = elt["d12"]
        if not elt.roadworks:
            if oneway == 'True':
                if node == elt.node2:
                    n.append((elt.node(node), float(elt['d9'])))
            else:
                n.append((elt.node(node), float(elt["d9"])))
    return n

def path(dest):
    if dest.pred == None:
        return [dest.id]
    return path(dest.pred) + [dest.id]

def distance(node1, node2):
    x1 = float(node1["d4"])
    y1 = float(node1["d3"])
    x2 = float(node2["d4"])
    y2 = float(node2["d3"])
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)