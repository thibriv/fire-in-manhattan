from math import sqrt, inf
import heapdict as hp
import graph_display as g

def initialisation(graph, dest): # dest est la liste des destinations
    n = len(dest)
    heap = [] # création de la liste de priorité
    it = [0 for k in range(n)]
    for node in graph.nodes():
        node.h = [inf for k in range(n)] # initialisation de la liste des heuristiques
        node.c = [inf for k in range(n)] # initialisation de la liste des coûts
        node.suc = [None for k in range(n)] # initialisation de la liste des successeurs
        node.close = [False for k in range(n)] # initialsiaiton de la liste des noeuds (pas parcouru)
    for k in range(n):
        d = dest[k]
        d.h[k] = 0
        d.c[k] = 0
        heap.append(hp.heapdict()) # ajout des sous-listes de priorité
        heap[k][d] = 0 # ajout des distances aux sous-listes
    return heap, it

def astar(graph, src, dest):
    heap, it = initialisation(graph, dest)
    while True: # tant que le programme tourne
        i = condition_priorite(it) # indice du minimum de it
        u = heap[i].popitem()[0] # on prend le noeud d'indice i de la liste de priorité
        u.close[i] = True # le noeud est parcouru
        if u == src: # si le noeud correspond à la source
            return (u.c[i], path(u, i), dest[i]) # retourne le coût, le chemin et la destination
        heuristique = [] # création d'une liste heuristique
        for (v, v_weight) in neighbours(graph, u):  # pour tous les voisins on recupère la longueur de l'arc
            current_cost = u.c[i] + v_weight
            v.color = g.COLOR_NODE_PAR[i]
            if not v.close[i]: # si le noeud n'est pas encore parcouru
                v.c[i] = current_cost
                v.h[i] = distance(v, src)
                heap[i][v] = v.h[i]
                heuristique.append(v.h[i]) # mise à jour de la liste heuristique
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