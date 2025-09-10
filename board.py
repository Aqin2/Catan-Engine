from globals import *
from entities import *
import numpy as np
from copy import copy
from player import Player
import json

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
    PORT_DIRS = [
        (Direction.NQ, Direction.R),
        (Direction.S, Direction.NQ),
        (Direction.NR, Direction.S),
        (Direction.Q, Direction.NR),
        (Direction.NS, Direction.Q),
        (Direction.R, Direction.NS)
    ]
    RESOURCES = [Resource.brick] * 3 + [Resource.wood] * 4 + [Resource.wool] * 4 \
        + [Resource.wheat] * 4 + [Resource.ore] * 3
    NUMBERS = [
        2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12
    ]
    PORTS = [
        [(0, None), (2, Resource.wool)],
        [(1, None)],
        [(0, None), (2, Resource.brick)],
        [(1, Resource.wood)],
        [(0, None), (2, Resource.wheat)],
        [(1, Resource.ore)]
    ]

    adj_lists_set = False

    def __init__(self, seed=None):
        #randomly initialize tile and number lists
        self.seed = seed
        self.random = np.random.default_rng(seed=seed)

        self.generate_board()
        self.build_dicts()
        self.build_adj_lists()
        
    #randomly generate a new board
    def generate_board(self):
        resources = np.array(Board.RESOURCES)
        numbers = np.array(Board.NUMBERS)
        port_data = copy(Board.PORTS)

        self.random.shuffle(resources)
        self.random.shuffle(numbers)
        self.random.shuffle(port_data)

        desert_idx = self.random.integers(19)
        resources = np.insert(resources, desert_idx, None)
        numbers = np.insert(numbers, desert_idx, -1)
        
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
                    #place tile
                    self.tiles.append(Tile(
                        cur_tile_coords.copy(),
                        tile_idx,
                        resources[tile_idx],
                        numbers[tile_idx]
                    ))
                    if resources[tile_idx] is None:
                        self.robber_tile = self.tiles[tile_idx]

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
        #end for

        #add ports
        self.ports: list[Port] = []
        port_idx = 0
        cur_tile_coords = Direction.QR * 2 * 3
        for i, tile_offset in enumerate(Board.TILE_OFFSETS):
            for port_pos, port_resource in port_data[i]:
                self.ports.append(Port(
                    cur_tile_coords + tile_offset * port_pos,
                    port_idx,
                    port_resource,
                    Board.PORT_DIRS[i if port_pos != 2 else (i + 1) % 6]
                ))
                port_idx += 1
        

    #dicts for fast access
    #dicts take a custom hash of the coords
    def build_dicts(self):
        self.tile_dict = dict()
        self.edge_dict = dict()
        self.node_dict = dict()
    
        for tile in self.tiles:
            self.tile_dict[Board.coords_hash(tile.coords)] = tile
        for edge in self.edges:
            self.edge_dict[Board.coords_hash(edge.coords)] = edge
        for node in self.nodes:
            self.node_dict[Board.coords_hash(node.coords)] = node

        self.node_port_dict = dict()
        for port in self.ports:
            for dir in port.dirs:
                self.node_port_dict[Board.coords_hash(port.coords + dir)] = port

    #build adjacency lists for fast access
    #these will always be the same between games so they are saved between instances of Board
    def build_adj_lists(self):
        if Board.adj_lists_set:
            return
        
        Board.edge_edge_list = []
        for edge in self.edges:
            adj = []
            for coords in edge.adj_edge_coords():
                hash = Board.coords_hash(coords)
                if hash in self.edge_dict.keys():
                    adj.append(self.edge_dict[hash].index)
            
            Board.edge_edge_list.append(adj)
                    
        Board.node_node_list: list[list[int]] = []
        for node in self.nodes:
            adj = []
            for coords in node.adj_node_coords():
                hash = Board.coords_hash(coords)
                if hash in self.node_dict.keys():
                    adj.append(self.node_dict[hash].index)
            Board.node_node_list.append(adj)

        Board.node_edge_list: list[list[int]] = []
        for node in self.nodes:
            adj = []
            for coords in node.adj_edge_coords():
                hash = Board.coords_hash(coords)
                if hash in self.edge_dict.keys():
                    adj.append(self.edge_dict[hash].index)
            Board.node_edge_list.append(adj)

        Board.edge_node_list: list[list[int]] = []
        for edge in self.edges:
            adj = []
            for coords in edge.adj_node_coords():
                hash = Board.coords_hash(coords)
                if hash in self.node_dict.keys():
                    adj.append(self.node_dict[hash].index)
            Board.edge_node_list.append(adj)

        Board.node_tile_list: list[list[int]] = []
        for node in self.nodes:
            adj = []
            for coords in node.adj_tile_coords():
                hash = Board.coords_hash(coords)
                if hash in self.tile_dict.keys():
                    adj.append(self.tile_dict[hash].index)
            Board.node_tile_list.append(adj)
        
        Board.tile_node_list: list[list[int]] = []
        for tile in self.tiles:
            adj = []
            for coords in tile.adj_node_coords():
                hash = Board.coords_hash(coords)
                if hash in self.node_dict.keys():
                    adj.append(self.node_dict[hash].index)
            Board.tile_node_list.append(adj)
        
        Board.adj_lists_set = True

        
    def place_structure(self, coords, player: Player, value, starting=False):
        node: Node = self.node_dict.get(Board.coords_hash(coords))
        if node is None:
            return False
        if value == 1:
            if not node.available:
                return False
            if not starting:
                has_road = False
                for adj_idx in Board.node_edge_list[node.index]:
                    if self.edges[adj_idx].player == player:
                        has_road = True
                        break
                if not has_road:
                    return False
        elif value == 2:
            #cant build cities initially
            if starting:
                return False
            if node.value != 1:
                return False
            if node.player != player:
                return False
            
        old_value = node.value

        for adj_idx in Board.node_tile_list[node.index]:
            tile = self.tiles[adj_idx]
            if tile.resource is not None:
                player.resources_gen[tile.number][tile.resource] += value - old_value

        node.place_structure(player, value)
        
        for adj_idx in Board.node_node_list[node.index]:
            self.nodes[adj_idx].available = False
        node.available = False
        
        return True
    
    def place_road(self, coords, player: Player):
        edge: Edge = self.edge_dict.get(Board.coords_hash(coords))
        if edge is None:
            return False
        if edge.player:
            return False
        
        #must place a road from an existing settlement or road,
        #road must not go through another players settlement
        for node_idx in Board.edge_node_list[edge.index]:
            node: Node = self.nodes[node_idx]
            #adjacent settlement/city
            if node.player == player:
                #place road
                edge.player = player
                return True
            
            #empty node
            elif node.player is None:
                for edge_idx in Board.node_edge_list[node.index]:
                    adj_edge = self.edges[edge_idx]
                    if adj_edge.player == player:
                        #place road
                        edge.player = player
                        return True
                    
            #if node is occupied by other player, cannot be built from that node
            
        return False

    def move_robber(self, coords):
        if self.robber_tile.coords == coords:
            return False
        tile: Tile = self.tile_dict.get(Board.coords_hash(coords), None)
        if tile is None:
            return False
        self.robber_tile = tile
        return True

    '''
    returns a json-serializable python obj.

    json obj format:
    {
        tiles: (string)[], //resource type or null for desert
        edges: (string | null)[], //player road name or null for no road

        nodes: { player: string | null, value: int }[]
        //player structure name or null for no structure,
        //value = 0 for none, 1 for settlement, 2 for city

        //the tile/edge/node with id i will be arr[i] for the respective array arr
    }
    '''
    def to_json_obj(self):
        obj = dict()

        obj['tiles'] = [
            {
                'resource': tile.resource.value if tile.resource else 'desert',
                'number': int(tile.number)
            }
            for tile in self.tiles
        ]
        obj['edges'] = [ edge.player.name if edge.player else None for edge in self.edges ]
        obj['nodes'] = [
            { 'player': node.player.name if node.player else None, 'value': node.value } for node in self.nodes
        ]
        obj['robber_tile'] = int(self.robber_tile.index)
        
        return obj

    @staticmethod
    def coords_hash(coords):
        return coords[0] * 256 + coords[1]