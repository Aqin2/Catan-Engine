from globals import *
from player import Player
import numpy as np

class Entity:
    def __init__(self, coords: np.ndarray, index: int):
        self.coords = coords
        self.index = index

class Node(Entity):
    NODE_OFFSETS = [
        Direction.Q,
        Direction.R,
        Direction.S
    ]
    EDGE_OFFSETS = [
        Direction.Q // 2,
        Direction.R // 2,
        Direction.S // 2
    ]
    def __init__(self, coords, index):
        super().__init__(coords, index)
        self.player: Player | None = None
        self.value = 0

        self.available = True
        
        #adj_nodes[i] is connected through adj_edges[i]
        self.adj_edges: list[Edge] = []
        self.adj_nodes: list[Node] = []

        self.adj_tiles: list[Tile] = []
        self.adj_port: Port = None


        if np.all(self.coords % 6 == 2):
            self.top = True
        elif np.all(self.coords % 6 == 4):
            self.top = False
        else:
            raise ValueError(f'Invalid node coordinates: {self.coords}')

    def adj_node_coords(self):
        if self.top:
            return [self.coords - offset for offset in Node.NODE_OFFSETS]
        else:
            return [self.coords + offset for offset in Node.NODE_OFFSETS]

    def adj_edge_coords(self):
        if self.top:
            return [self.coords - offset for offset in Node.EDGE_OFFSETS]
        else:
            return [self.coords + offset for offset in Node.EDGE_OFFSETS]
        
    def adj_tile_coords(self):
        #same as node offsets but in the other directions
        if self.top:
            return [self.coords + offset for offset in Node.NODE_OFFSETS]
        else:
            return [self.coords - offset for offset in Node.NODE_OFFSETS]


class Edge(Entity):
    EDGE_OFFSETS = [
        Direction.RS,
        Direction.SQ,
        Direction.QR,
    ]
    NODE_OFFSETS = [
        Direction.Q // 2,
        Direction.R // 2,
        Direction.S // 2
    ]
    def __init__(self, coords, index):
        super().__init__(coords, index)
        self.player = None

        i = np.where(self.coords % 6 == 0)
        assert len(i[0]) == 1, f'Invalid edge coordinates: {self.coords}'
        self.dir = i[0][0]

        #self.adj_edges[i] is connected through self.adj_nodes[i // 2]
        self.adj_edges: list[Edge] = []
        self.adj_nodes: list[Node] = []

    def place_road(self, player: Player):
        self.player = player

    def adj_edge_coords(self):
        adj_coords = []
        for i, offset in enumerate(Edge.EDGE_OFFSETS):
            if i == self.dir:
                continue
            adj_coords.append(self.coords + offset)
            adj_coords.append(self.coords - offset)
        
        return adj_coords
    
    def adj_node_coords(self):
        return [
            self.coords + Edge.NODE_OFFSETS[self.dir],
            self.coords - Edge.NODE_OFFSETS[self.dir]
        ]


class Tile(Entity):
    NODE_OFFSETS = [
        Direction.Q,
        Direction.NS,
        Direction.R,
        Direction.NQ,
        Direction.S,
        Direction.NR
    ]

    def __init__(self, coords, index, resource: Resource, number: int):
        super().__init__(coords, index)
        self.resource = resource
        self.number = number

        self.adj_nodes: list[Node] = []

    def adj_node_coords(self):
        return [ self.coords + offset for offset in Tile.NODE_OFFSETS ]

class Port(Entity):
    def __init__(self, coords, index, resource: Resource, dirs: tuple[np.ndarray]):
        super().__init__(coords, index)
        self.resource = resource
        self.dirs = dirs

        self.rate = 3 if self.resource is None else 2