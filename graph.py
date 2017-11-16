from collections import deque

class Node(object):
    """docstring for Node."""
    def __init__(self, name):
        self.name = name
        self.adj = {}
        self.incAdj = {}
        self.numC = 0
        self.rank = 0.0

    def insertAdj(self, node, weight):
        self.adj[node.name] = [weight, node]
        node.incAdj[self.name] = self
        self.numC += 1

    def updateRank(self, d):
        i = 0
        for node in self.incAdj.values():
            i += node.rank / node.numC
        self.rank = (1 - d) + (d) * i

    def toString(self):
        return str(self.name)

class graph(object):
    """docstring for Graph."""
    def __init__(self):
        self.nodes = {}
        self.size = 0

    def insert(self, node):
        self.nodes[node.name] = node
        self.size += 1
