import numpy as np
from enum import Enum

class Resource(Enum):
    BRICK =  0
    WOOD =  1
    WOOL = 2
    WHEAT =  3
    ORE = 4
    DESERT = 5

class Direction():
    #dirs from center of tile to corner of tile
    Q = np.array([4, -2, -2])
    R = np.array([-2, 4, -2])
    S = np.array([-2, -2, 4])
    NQ = -Q
    NR = -R
    NS = -S
    
    #dirs from center of tile to edge of tile
    QR = (Q - R) // 2
    RS = (R - S) // 2
    SQ = (S - Q) // 2
    NQR = -QR
    NRS = -RS
    NSQ = -SQ


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
    def __init__(self, coords, index):
        super().__init__(coords, index)
        self.player = None
        self.value = 0

        if np.all(self.coords % 6 == 2):
            self.top = True
        elif np.all(self.coords % 6 == 4):
            self.top = False
        else:
            raise ValueError(f'Invalid node coordinates: {self.coords}')
    
    def place_structure(self, player, value):
        self.player = player
        self.value = value

    def adj_node_coords(self):
        if self.top:
            return [self.coords - offset for offset in Node.NODE_OFFSETS]
        else:
            return [self.coords + offset for offset in Node.NODE_OFFSETS]



class Edge(Entity):
    EDGE_OFFSETS = [
        Direction.RS,
        Direction.SQ,
        Direction.QR,
    ]
    def __init__(self, coords, index):
        super().__init__(coords, index)
        self.player = None

        i = np.where(self.coords % 6 == 0)
        assert len(i[0]) == 1, f'Invalid edge coordinates: {self.coords}'
        self.dir = i[0][0]

    def place_road(self, player):
        self.player = player

    def adj_edge_coords(self):
        adj_coords = []
        for i, offset in enumerate(Edge.EDGE_OFFSETS):
            if i == self.dir:
                continue
            adj_coords.append(self.coords + offset)
            adj_coords.append(self.coords - offset)
        
        return adj_coords

class Tile(Entity):
    def __init__(self, coords, index, resource, number):
        super().__init__(coords, index)
        self.resource = resource
        self.number = number

class Board:
    BOARD_SIZE = 3
    TILE_OFFSETS = [
        Direction.RS * 2,
        Direction.NQR * 2,
        Direction.SQ * 2,
        Direction.NRS * 2,
        Direction.QR * 2,
        Direction.NSQ * 2,
    ]
    EDGE_OFFSETS = [
        Direction.QR,
        Direction.NSQ,
        Direction.RS,
        Direction.NQR,
        Direction.SQ,
        Direction.NRS
    ]
    NODE_OFFESTS = [
        Direction.Q,
        Direction.NS,
        Direction.R,
        Direction.NQ,
        Direction.S,
        Direction.NR
    ]
    RESOURCES = [Resource.BRICK] * 3 + [Resource.WOOD] * 4 + [Resource.WOOL] * 4 \
        + [Resource.WHEAT] * 4 + [Resource.ORE] * 3
    NUMBERS = [
        2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12
    ]

    def __init__(self, seed=None):
        #randomly initialize tile and number lists
        self.seed = seed

        self.generate_board()
        self.build_dicts()
        self.build_adj_lists()
        

    def generate_board(self):
        np.random.seed(self.seed)
        resources = np.array(Board.RESOURCES)
        numbers = np.array(Board.NUMBERS)
        np.random.shuffle(resources)
        np.random.shuffle(numbers)

        desert_idx = np.random.randint(19)
        resources = np.insert(resources, desert_idx, Resource.DESERT)
        numbers = np.insert(resources, desert_idx, -1)
        
        #add initial tiles, edges and nodes
        cur_tile_coords = np.array([0, 0, 0])

        self.tiles = [ Tile(cur_tile_coords.copy(), 0, resources[0], numbers[0]) ]
        self.edges = [
            Edge(
                cur_tile_coords + edge_offset, 
                idx,
            ) for idx, edge_offset in enumerate(Board.EDGE_OFFSETS)
        ]
        self.nodes: list[Node] = [
            Node(cur_tile_coords + node_offset, idx) for idx, node_offset in enumerate(Board.NODE_OFFESTS)
        ]

        tile_idx = len(self.tiles)
        edge_idx = len(self.edges)
        node_idx = len(self.nodes)

        #add tiles, edges, and nodes in order, spiraling out from center
        for rad in range(1, Board.BOARD_SIZE):
            cur_tile_coords += Direction.QR * 2
            for i, tile_offset in enumerate(Board.TILE_OFFSETS):
                for j in range(rad):
                    cur_tile_coords += tile_offset
                    self.tiles.append(Tile(
                        cur_tile_coords.copy(),
                        tile_idx,
                        resources[tile_idx],
                        numbers[tile_idx]
                    ))

                    tile_idx += 1
                    
                    #place edges and nodes
                    for k in range(i, i + (4 if j == rad - 1 else 3)):
                        self.edges.append(Edge(
                            cur_tile_coords + Board.EDGE_OFFSETS[k % 6], edge_idx,
                        ))
                        edge_idx += 1
                    for k in range(i, i + (3 if j == rad - 1 else 2)):
                        self.nodes.append(Node(
                            cur_tile_coords + Board.NODE_OFFESTS[k % 6], node_idx,
                        ))
                        node_idx += 1

    def build_dicts(self):
        self.tile_dict = dict()
        self.edge_dict = dict()
        self.node_dict = dict()

        for tile in self.tiles:
            self.tile_dict[Board.coords_hash(tile.coords)] = tile.index
        for edge in self.edges:
            self.edge_dict[Board.coords_hash(edge.coords)] = edge.index
        for node in self.nodes:
            self.node_dict[Board.coords_hash(node.coords)] = node.index

    def build_adj_lists(self):
        self.edge_adj_list = []
        for edge in self.edges:
            adj = []
            for coords in edge.adj_edge_coords():
                hash = Board.coords_hash(coords)
                if hash in self.edge_dict.keys():
                    adj.append(self.edge_dict[hash])
            
            self.edge_adj_list.append(adj)
                    
        self.node_adj_list = []
        for node in self.nodes:
            adj = []
            for coords in node.adj_node_coords():
                hash = Board.coords_hash(coords)
                if hash in self.node_dict.keys():
                    adj.append(self.node_dict[hash])
            self.node_adj_list.append(adj)
        
    def place_structure(self, coords, player, value):
        node_idx = self.node_dict[Board.coords_hash(coords)]
        self.nodes[node_idx].place_structure(player, value)

    def place_road(self, coords, player):
        edge_idx = self.edge_dict[Board.coords_hash(coords)]
        self.edges[edge_idx].place_road(player)

    @staticmethod
    def coords_hash(coords):
        return coords[0] * 256 + coords[1]
    