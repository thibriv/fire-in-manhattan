import heapdict as hp
from math import inf
import graph_display as g

#renvoie les voisins de node dans le graph ainsi que la longueur de l'arrete entre node et son voisin
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

#renvoie l'id des points du chemin pour atteindre dest
def path(node,bool):
    if bool:
       if node.pred == None:
          return [node.id]
       return path(node.pred,True) + [node.id]
    else:
        if node.suc == None:
            return [node.id]
        return [node.id]+path(node.suc,False)

#ajoute les attributs necessaires aux noeuds et initialise la source et la dest
def initialisation_node(graph,src,dest):
    for node in graph.nodes():
        node.dist = [inf,inf]
        node.suc = None
        node.pred = None
        node.close = [False,False]
    src.dist[0] = 0
    dest.dist[1] = 0

#revoie la liste L sans doublon
def listonly(L):
    setlist = []
    for elt in L:
        if elt not in setlist:
            setlist.append(elt)
    return setlist

#Calcul le plus court chemin entre src et dest dans graph
def dijkstra(graph, src, dest):
    def dijkstra_int(heap,bool,mindist,nc):
        u=heap.popitem()[0]
        if bool:
            it[0]-=1
            u.color = g.COLOR_NODE_PAR[0]
            u.close[0] = True
            for (v, vweight) in neighbours(graph,u,bool): #pour tout les voisins on recupère la longueur de l'arc
                 if not v.close[0]:# si le noeud n'a pas encore été visité
                    dist = u.dist[0] + vweight
                    if v.close[1]:
                        if dist + v.dist[1] < mindist:
                            mindist = dist + v.dist[1]
                            nc = v  # noeud charniere
                    if v.dist[0] > dist:
                       v.dist[0] = dist
                       v.pred = u
                       heapfront[v] = dist
                       it[0]+=1
            return nc,mindist
        else:
            it[1]-=1
            u.close[1] = True
            u.color = g.COLOR_NODE_PAR[25]
            for (v, vweight) in neighbours(graph,u,bool): #pour tout les voisins on recupère la longueur de l'arc
                 if not v.close[1]:# si le noeud n'a pas encore été visité
                    dist = u.dist[1] + vweight
                    if v.close[0]:
                        if dist + v.dist[0] < mindist:
                            mindist = dist + v.dist[0]
                            nc = v  # noeud charniere
                    if v.dist[1] > dist:
                       v.dist[1] = dist
                       v.suc = u
                       heapback[v]=dist
                       it[1]+=1
            return nc,mindist
    initialisation_node(graph,src,dest)
    it=[0,0]
    heapfront = hp.heapdict() #liste priorité avant
    heapback = hp.heapdict() #liste priorité arrière
    heapfront[src] = 0
    heapback[dest] = 0
    nc = None
    mindist = inf
    while True:
        if heapfront.peekitem()[1]+heapback.peekitem()[1]>=mindist:
            return (sum(nc.dist),listonly(path(nc,True)+path(nc,False)))#mindist et reconstruire trajet depuis noeud charniere
        if it[0]>it[1]: #autre condition possible sur len des liste de priorité
            nc,mindist = dijkstra_int(heapback,False,mindist,nc)
        else:
            nc,mindist = dijkstra_int(heapfront,True,mindist,nc)