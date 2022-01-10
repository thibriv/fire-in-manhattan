from math import sqrt, inf
import heapdict as hp
import graph_display as g

def astar(graph, src, dest):
    def astar_int(heap, bool):
        u = heap.popitem()[0]
        if bool:
            it[0] += 1
            u.color = g.COLOR_NODE_PAR[1]
            u.close[0] = True
            for (v, v_weight) in neighbours(graph, u, bool):  # pour tout les voisins on recupère la longueur de l'arc
                current_cost = u.c[0] + v_weight
                if not v.close[0]:
                    v.c[0] = current_cost
                    v.h[0] = distance(v, dest)
                    heapfront[v] = v.h[0]
                    v.pred = u
            return
        else:
            it[1] += 1
            u.close[1] = True
            u.color = g.COLOR_NODE_PAR[0]
            for (v, v_weight) in neighbours(graph, u, bool):  # pour tout les voisins on recupère la longueur de l'arc
                current_cost = u.c[1] + v_weight
                if not v.close[1]:
                    v.c[1] = current_cost
                    v.h[1] = distance(v, src)
                    heapback[v] = v.h[1]
                    v.suc = u
            return

    for node in graph.nodes():
        node.h = [inf, inf]
        node.suc = None
        node.pred = None
        node.close = [False, False]
        node.c = [inf, inf]
    it = [0, 0]
    src.h[0] = 0
    dest.h[1] = 0
    src.c[0] = 0
    dest.c[1] = 0
    heapfront = hp.heapdict()  # liste priorité avant
    heapback = hp.heapdict()  # liste priorité arrière
    heapfront[src] = 0
    heapback[dest] = 0
    while True:
        peakf = heapfront.peekitem()[0]
        peakb = heapback.peekitem()[0]
        if peakf.close[1]:
            astar_int(heapfront, True)
            return (sum(peakf.c), listonly(
                path(peakf, True) + path(peakf, False)))  # mindist et reconstruire trajet depuis noeud charniere
        if peakb.close[0]:
            astar_int(heapback, False)
            return (sum(peakb.c), listonly(
                path(peakb, True) + path(peakb, False)))  # mindist et reconstruire trajet depuis noeud charniere
        if it[0] > it[1]:  # autre condition possible sur len des liste de priorité
            astar_int(heapback, False)
        else:
            astar_int(heapfront, True)

def listonly(L):
    setlist = []
    for elt in L:
        if elt not in setlist:
            setlist.append(elt)
    return setlist

def neighbours(graph, node, bool):
    n = []
    k = graph.nodes().index(node)
    for elt in graph.nodes()[k].edges():
        oneway = elt["d12"]
        if not elt.roadworks:
            if oneway == 'True':
                if bool:
                    if node == elt.node2:
                        n.append((elt.node(node), float(elt['d9'])))
                else:
                    if node == elt.node1:
                        n.append((elt.node(node), float(elt['d9'])))
            else:
                n.append((elt.node(node), float(elt["d9"])))
    return n

def path(node, bool):
    if bool:
        if node.pred == None:
            return [node.id]
        return path(node.pred, True) + [node.id]
    else:
        if node.suc == None:
            return [node.id]
        return [node.id] + path(node.suc, False)

def distance(node1, node2):
    x1 = float(node1["d4"])
    y1 = float(node1["d3"])
    x2 = float(node2["d4"])
    y2 = float(node2["d3"])
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
