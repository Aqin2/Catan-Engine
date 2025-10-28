from globals import *
from entities import *
import numpy as np
from copy import copy
from player import Player

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
    SETTLEMENT_COST = {
        Resource.brick: 1,
        Resource.wood: 1,
        Resource.wool: 1,
        Resource.wheat: 1
    }
    CITY_COST = {
        Resource.wheat: 2,
        Resource.ore: 3,
    }
    ROAD_COST = {
        Resource.brick: 1,
        Resource.wood: 1
    }
    adj_lists_set = False

    def __init__(self, players: list[Player], seed=None):
        self.build_board()
        self.build_dicts()
        self.build_adj_lists()

        self.players = players
        self.reset(seed)
        
    def reset(self, seed):
        #reset player entities
        for edge in self.edges:
            edge.player = None
        for node in self.nodes:
            node.player = None
            node.value = 0
            node.adj_port = None

        #generate tile resources and numbers
        self.seed = seed
        self.random = np.random.default_rng(seed=seed)

        resources = np.array(Board.RESOURCES)
        numbers = np.array(Board.NUMBERS)

        self.random.shuffle(resources)
        self.random.shuffle(numbers)

        desert_idx = self.random.integers(19)
        resources = np.insert(resources, desert_idx, None)
        numbers = np.insert(numbers, desert_idx, -1)

        for i, tile in enumerate(self.tiles):
            tile.resource = resources[i]
            tile.number = numbers[i]
        
        self.robber_tile = self.tiles[desert_idx]

        #add ports
        port_data = copy(Board.PORTS)
        self.random.shuffle(port_data)
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

        for port in self.ports:
            for dir in port.dirs:
                node: Node = self.node_dict.get(Board.coords_hash(port.coords + dir))
                if node:
                    node.adj_port = port
    
    #the build functions should only be called once
    #to reset the board for a new game, call reset()
    #this method builds the board graph structure
    #it does not set resources or numbers on tiles
    def build_board(self):
        #add initial tiles, edges and nodes
        cur_tile_coords = np.array([0, 0, 0])

        self.tiles = [ Tile(cur_tile_coords.copy(), 0, None, None) ]
        self.robber_tile = self.tiles[0]

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
                        None,
                        None
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
        #end for

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


    def build_adj_lists(self):
        for edge in self.edges:
            for node_coords in edge.adj_node_coords():
                node: Node = self.node_dict[Board.coords_hash(node_coords)]
                for edge_coords in node.adj_edge_coords():
                    adj_edge = self.edge_dict.get(Board.coords_hash(edge_coords))
                    if adj_edge and adj_edge != edge:
                        edge.adj_edges.append(adj_edge)
                edge.adj_nodes.append(node)

        for node in self.nodes:
            for edge_coords in node.adj_edge_coords():                
                adj_edge = self.edge_dict.get(Board.coords_hash(edge_coords))
                if adj_edge:
                    node.adj_edges.append(adj_edge)
            for node_coords in node.adj_node_coords():
                adj_node = self.node_dict.get(Board.coords_hash(node_coords))
                if adj_node:
                    node.adj_nodes.append(adj_node)
            for tile_coords in node.adj_tile_coords():
                adj_tile = self.tile_dict.get(Board.coords_hash(tile_coords))
                if adj_tile:
                    node.adj_tiles.append(adj_tile)

        for tile in self.tiles:
            for node_coords in tile.adj_node_coords():
                adj_node = self.node_dict.get(Board.coords_hash(node_coords))
                if adj_node:
                    tile.adj_nodes.append(adj_node)

    def place_settlement(self, node_idx: int, cur_player: Player, starting=False):
        #check move legality for board
        if node_idx < 0 or node_idx >= len(self.nodes):
            return False
        if not cur_player.available_settlements[node_idx] and not starting:
            return False
        node = self.nodes[node_idx]
        if not node.available:
            return False
        if not starting:
            if not cur_player.can_afford(Board.SETTLEMENT_COST):
                return False
            #pay cost
            cur_player.pay_cost(Board.SETTLEMENT_COST)
        
        #update board
        node.player = cur_player
        node.value = 1

        #player allowed move updates
        node.available = False
        for player in self.players:
            player.available_settlements[node_idx] = False

        for adj_node in node.adj_nodes:
            for player in self.players:
                player.available_settlements[adj_node.index] = False
            adj_node.available = False
        
        for adj_edge in node.adj_edges:
            if not adj_edge.player:
                cur_player.available_roads[adj_edge.index] = True

        cur_player.available_cities[node_idx] = True
        cur_player.rem_settlements -= 1
        cur_player.n_settlements += 1
        #player resource generation update
        for tile in node.adj_tiles:
            if tile.resource:
                cur_player.resources_gen[tile.number][tile.resource] += 1
        
        #player bank trade rate / port update
        port = node.adj_port
        if port:
            if port.resource:
                cur_player.bank_trade_rates[port.resource] = 2
            else:
                for resource in Resource:
                    cur_player.bank_trade_rates[resource] = min(3, cur_player.bank_trade_rates[resource])
        return True

    def place_city(self, node_idx: int, cur_player: Player):
        #check move legality for board
        if node_idx < 0 or node_idx >= len(self.nodes):
            return False
        node = self.nodes[node_idx]
        if not cur_player.available_cities[node_idx]:
            return False
        if not cur_player.can_afford(Board.CITY_COST):
            return False

        #pay cost
        cur_player.pay_cost(Board.CITY_COST)

        #update board
        node.value = 2

        #player allowed move update
        cur_player.available_cities[node_idx] = False
        cur_player.rem_cities -= 1
        cur_player.n_settlements -= 1
        cur_player.n_cities += 1

        #player resource generation update
        for tile in node.adj_tiles:
            if tile.resource:
                cur_player.resources_gen[tile.number][tile.resource] += 1

        #no need for bank trade rate update
        #upgrading to a city doesnt access new ports
        return True

    def place_road(self, edge_idx: int, cur_player: Player, starting=False):
        if edge_idx < 0 or edge_idx >= len(self.edges):
            return False
        if not cur_player.available_roads[edge_idx]:
            return False
        edge = self.edges[edge_idx]
        if cur_player.road_dev_count == 0 and not starting:
            if not cur_player.can_afford(Board.ROAD_COST):
                return False
            cur_player.pay_cost(Board.ROAD_COST)
        
        edge.player = cur_player

        for player in self.players:
            player.available_roads[edge.index] = False

        for i, adj_edge in enumerate(edge.adj_edges):
            if adj_edge.player:
                continue
            if edge.adj_nodes[i // 2].player is None or edge.adj_nodes[i // 2].player == cur_player:
                cur_player.available_roads[adj_edge.index] = True
            
        for adj_node in edge.adj_nodes:
            if adj_node.available:
                cur_player.available_settlements[adj_node.index] = True

        return True
            
    def move_robber(self, tile_idx: int):
        if tile_idx < 0 or tile_idx >= len(self.tiles):
            return False
        if self.robber_tile.index == tile_idx:
            return False
        self.robber_tile = self.tiles[tile_idx]
        return True
        
    def check_longest_road(self, player: Player):
        visited = [False] * len(self.edges)
        def dfs(u: int, l: int):
            visited[u] = True
            edge = self.edges[u]
            for i, adj_edge in enumerate(edge.adj_edges):
                if edge.adj_nodes[i // 2].player != player and edge.adj_nodes[i // 2]:
                    continue
                if not visited[adj_edge.index] and adj_edge.player == player:
                    l = max(l, dfs(adj_edge.index, l + 1))
            visited[u] = False
            return l
        
        max_len = -1
        for edge_idx in player.roads:
            max_len = max(max_len, dfs(edge_idx, 0))
        
        player.longest_road_len = max_len

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
    
    def get_obs(self, player_idx, num_players):
        obs = dict()
        obs['nodes'] = np.zeros((54, num_players), dtype=np.int32)
        for node in self.nodes:
            if node.player:
                obs['nodes'][node.index][(node.player.index - player_idx) % num_players] = node.value
        obs['edges'] = np.zeros((72, num_players), dtype=np.int32)
        for edge in self.edges:
            if edge.player:
                obs['edges'][edge.index][(edge.player.index - player_idx) % num_players] = 1
        obs['tile_types'] = np.zeros((19, 6), dtype=np.int32)
        obs['tile_nums'] = np.zeros((19,), dtype=np.int32)
        for tile in self.tiles:
            if tile.resource:
                obs['tile_types'][tile.index][RESOURCE_TYPES_DICT[tile.resource]] = 1
                obs['tile_nums'][tile.index] = tile.number
            else:
                obs['tile_types'][tile.index][0] = 1
                obs['tile_nums'][tile.index] = 0
        obs['robber_tile'] = np.zeros((19,), dtype=np.int32)
        obs['robber_tile'][self.robber_tile.index] = 1
        
        return obs

    @staticmethod
    def coords_hash(coords):
        return coords[0] * 256 + coords[1]
    