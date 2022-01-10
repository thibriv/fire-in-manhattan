import heapdict as hp
from math import inf
import graph_display as g

# renvoie les voisins de node dans le graph ainsi que la longueur de l'arrete entre node et son voisin
def neighbours(graph, node, i):
    n = []
    k = graph.nodes().index(node)
    for elt in graph.nodes()[k].edges():
        oneway = elt["d12"]
        if not elt.roadworks:
            if oneway == 'True':
                if i == 0:
                    if node == elt.node2:
                        n.append((elt.node(node), float(elt['d9'])))
                else:
                    if node == elt.node1:
                        n.append((elt.node(node), float(elt['d9'])))
            else:
                n.append((elt.node(node), float(elt["d9"])))
    return n

# renvoie l'id des points du chemin pour atteindre dest
def path(node, i):
    if i == 0:
        if node.pred == None:
            return [node.id]
        return path(node.pred, i) + [node.id]
    else:
        if node.suc[i - 1] == None:
            return [node.id]
        return [node.id] + path(node.suc[i - 1], i)

# revoie la liste L sans doublon
def listonly(L):
    setlist = []
    for elt in L:
        if elt not in setlist:
            setlist.append(elt)
    return setlist

# initialise le programme
def initialisation(graph, src, d):
    heap = []
    n = len(d) + 1
    for node in graph.nodes():
        node.dist = [inf for k in range(n)]
        node.pred = None
        node.suc = [None for k in range(n)]
        node.close = [False for k in range(n)]
    src.dist[0] = 0
    for i in range(n):
        h = hp.heapdict()
        if i != 0:
            dest = d[i - 1]
            dest.dist[i] = 0
            h[dest] = 0
        heap.append(h)
    heap[0][src] = 0
    it = [1 for k in range(n)]
    list_nc = [None for k in range(n)]
    mindist = [inf for k in range(n)]
    return heap, it, list_nc, mindist

def condition_priorite(it):
    m = min(it)
    i_min = it.index(m)
    return i_min

def condition_arret(heap, mindist):
    for i in range(1, len(heap)):
        if heap[0].peekitem()[1] + heap[i].peekitem()[1] >= mindist[i]:
            return (True, i)
    return (False, 0)

def frontier_meeting(v, dist, mindist, list_nc):
    for i in range(1, len(list_nc)):
        if v.close[i]:
            if dist + v.dist[i] < mindist[i]:
                mindist[i] = dist + v.dist[i]
                list_nc[i] = v  # noeud charniere
    return

# Calcul le plus court chemin entre src et dest dans graph
def dijkstra(graph, src, d):
    def dijkstra_int(heap, mindist, list_nc, i):
        u = heap[i].popitem()[0]
        if i == 0:
            it[0] -= 1
            u.color = g.COLOR_NODE_PAR[0]
            u.close[0] = True
            for (v, vweight) in neighbours(graph, u, i):  # pour tout les voisins on recupère la longueur de l'arc
                if not v.close[0]:  # si le noeud n'a pas encore été visité
                    dist = u.dist[0] + vweight
                    frontier_meeting(v, dist, mindist, list_nc)
                    if v.dist[0] > dist:
                        v.dist[0] = dist
                        v.pred = u
                        heap[0][v] = dist
                        it[0] += 1
            return mindist,list_nc
        else:
            it[i] -= 1
            u.close[i] = True
            u.color = g.COLOR_NODE_PAR[(i - 1)%len(g.COLOR_NODE_PAR)]
            for (v, vweight) in neighbours(graph, u, i):  # pour tout les voisins on recupère la longueur de l'arc
                if not v.close[i]:  # si le noeud n'a pas encore été visité
                    dist = u.dist[i] + vweight
                    if v.close[0]:
                        if dist + v.dist[0] < mindist[i]:
                            mindist[i] = dist + v.dist[0]
                            list_nc[i] = v  # noeud charniere
                    if v.dist[i] > dist:
                        v.dist[i] = dist
                        v.suc[i - 1] = u
                        heap[i][v] = dist
                        it[i] += 1
            return mindist,list_nc

    heap, it, list_nc, mindist = initialisation(graph, src, d)
    while True:
        arret = condition_arret(heap, mindist)
        if arret[0]:
            i_arr = arret[1]
            nc = list_nc[i_arr]
            return (nc.dist[0] + nc.dist[i_arr], listonly(path(nc, 0) + path(nc, i_arr)),
                    d[i_arr - 1])  # mindist et reconstruire trajet depuis noeud charniere
        i = condition_priorite(it)
        mindist,list_nc=dijkstra_int(heap, mindist, list_nc, i)