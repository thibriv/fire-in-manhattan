from math import sqrt, inf
import heapdict as hp
import graph_display as g

def initialisation(graph, dest): # dest est la liste des destinations
    n = len(dest)
    heap = [] # creation of the heapqueue
    it = [0 for k in range(n)]
    for node in graph.nodes():
        node.h = [inf for k in range(n)] # initialization of the heuristics list
        node.c = [inf for k in range(n)] # initialization of the costs list
        node.suc = [None for k in range(n)] # initialization of the successors list
        node.close = [False for k in range(n)] # initializaiton of the non-explored nodes list
    for k in range(n):
        d = dest[k]
        d.h[k] = 0
        d.c[k] = 0
        heap.append(hp.heapdict()) # add of the sub-heapqueues
        heap[k][d] = 0 # add of the distance to the sub-lists
    return heap, it

def astar(graph, src, dest):
    heap, it = initialisation(graph, dest)
    while True: # while the program is running
        i = condition_priorite(it) # min index of it
        u = heap[i].popitem()[0] # we take the node of index i in the heapqueue
        u.close[i] = True # node is already explored
        if u == src: # if the node is the source
            return (u.c[i], path(u, i), dest[i]) # returns the cost, path and destination
        heuristique = [] # creation of the heuristics list
        for (v, v_weight) in neighbours(graph, u):  # for all neighbours, we get the length of the edge
            current_cost = u.c[i] + v_weight
            v.color = g.COLOR_NODE_PAR[i]
            if not v.close[i]: # if the node had not been explored yet
                v.c[i] = current_cost
                v.h[i] = distance(v, src)
                heap[i][v] = v.h[i]
                heuristique.append(v.h[i]) # update of the heuristics list
                v.suc[i] = u
        it[i] = min(heuristique)

def condition_priorite(it):
    m = min(it)
    i_min = it.index(m)
    return i_min

def neighbours(graph, node):
    n = []
    k = graph.nodes().index(node)
    for elt in graph.nodes()[k].edges():
        oneway = elt["d12"]
        if not elt.roadworks:
            if oneway == 'True':
                if node == elt.node1:
                    n.append((elt.node(node), float(elt['d9'])))
            else:
                n.append((elt.node(node), float(elt["d9"])))
    return n

def path(node, i):
    if node.suc[i] == None:
        return [node.id]
    return [node.id] + path(node.suc[i], i)

def distance(node1, node2):
    x1 = float(node1["d4"])
    y1 = float(node1["d3"])
    x2 = float(node2["d4"])
    y2 = float(node2["d3"])
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def listonly(L):
    setlist = []
    for elt in L:
        if elt not in setlist:
            setlist.append(elt)
    return setlist