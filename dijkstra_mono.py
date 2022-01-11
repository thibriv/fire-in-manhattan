from math import inf
import heapdict as hp
import graph_display as g
import time

def dijkstra(graph, src, dest):
    print(len(graph.nodes()))
    time1 = time.time()
    for node in graph.nodes():
        node.close = False
        node.pred = None
        node.dist = inf
    src.dist = 0
    src.pred = None
    heap = hp.heapdict()
    heap[src] = 0
    i=0
    while heap:
        i+=1
        node = heap.popitem()[0]  # we take the first item of the heapqueue
        node.close = True
        node.color = g.COLOR_NODE_PAR[0]  # coloration of the node
        if node in dest:  # if the node is the destination then end of the algorithm
            return (node.dist, path(node), node)
        for (v, vweight) in neighbours(graph, node):  # for all neighbours, we get the length of the edge
            if not v.close:
                dist = node.dist + vweight
                if v.dist > dist:
                    v.dist = dist
                    v.pred = node
                    heap[v] = dist
    time2 = time.time()
    print("temps execute"+str(time2-time1))
    print(i)

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