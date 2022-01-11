import heapdict as hp
from math import inf
import graph_display as g

def neighbours(graph, node, bool):
    """
    returns the neighbours of node in the graph and the length of the edgebetween node and its neighbour
    """
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

def path(node,bool):
    """
    returns the id of the nodes from the path to destination
    """
    if bool:
       if node.pred == None:
          return [node.id]
       return path(node.pred,True) + [node.id]
    else:
        if node.suc == None:
            return [node.id]
        return [node.id]+path(node.suc,False)

def initialisation_node(graph,src,dest):
    """
    initialize the mandatory attributes to the nodes and initialize the source and the destination
    """
    for node in graph.nodes():
        node.dist = [inf,inf]
        node.suc = None
        node.pred = None
        node.close = [False,False]
    src.dist[0] = 0
    dest.dist[1] = 0

def listonly(L):
    """
    returns the list L without twice the same element
    """
    setlist = []
    for elt in L:
        if elt not in setlist:
            setlist.append(elt)
    return setlist

def dijkstra(graph, src, dest):
    """
    calculate the shortest path from src to dest in graph
    """
    def dijkstra_int(heap,bool,mindist,nc):
        u=heap.popitem()[0]
        if bool:
            it[0]-=1
            u.color = g.COLOR_NODE_PAR[0]
            u.close[0] = True
            for (v, vweight) in neighbours(graph,u,bool): # for all neighbours, we get the length of the edge
                 if not v.close[0]:# if the node had not been explored yet
                    dist = u.dist[0] + vweight
                    if v.close[1]:
                        if dist + v.dist[1] < mindist:
                            mindist = dist + v.dist[1]
                            nc = v  # bridge node
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
            for (v, vweight) in neighbours(graph,u,bool): # for all neighbours, we get the length of the edge
                 if not v.close[1]:# if the node had not been explored yet
                    dist = u.dist[1] + vweight
                    if v.close[0]:
                        if dist + v.dist[0] < mindist:
                            mindist = dist + v.dist[0]
                            nc = v  # bridge node
                    if v.dist[1] > dist:
                       v.dist[1] = dist
                       v.suc = u
                       heapback[v]=dist
                       it[1]+=1
            return nc,mindist
    initialisation_node(graph,src,dest)
    it=[0,0]
    heapfront = hp.heapdict() #front heapqueue
    heapback = hp.heapdict() #back heapqueu
    heapfront[src] = 0
    heapback[dest] = 0
    nc = None
    mindist = inf
    while True:
        if heapfront.peekitem()[1]+heapback.peekitem()[1]>=mindist:
            return (sum(nc.dist),listonly(path(nc,True)+path(nc,False)))#mindist and construction of the path from bridge node
        if it[0]>it[1]: #other possible condition on 'len' of the heapqueues
            nc,mindist = dijkstra_int(heapback,False,mindist,nc)
        else:
            nc,mindist = dijkstra_int(heapfront,True,mindist,nc)