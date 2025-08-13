import numpy as np
from enum import Enum
from copy import copy
from collections import deque

#game globals
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

#game entitiess
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
        self.player = None
        self.value = 0

        self.available = True

        if np.all(self.coords % 6 == 2):
            self.top = True
        elif np.all(self.coords % 6 == 4):
            self.top = False
        else:
            raise ValueError(f'Invalid node coordinates: {self.coords}')
    
    def place_structure(self, player: str, value: int):
        self.player = player
        self.value = value

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

    def place_road(self, player: str):
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
    def __init__(self, coords, index, resource: Resource, number: int):
        super().__init__(coords, index)
        self.resource = resource
        self.number = number

class Port(Entity):
    def __init__(self, coords, index, resource: Resource, dirs: tuple[np.ndarray]):
        super().__init__(coords, index)
        self.resource = resource
        self.dirs = dirs

        self.rate = 3 if self.resource is None else 2

#game board
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
    RESOURCES = [Resource.BRICK] * 3 + [Resource.WOOD] * 4 + [Resource.WOOL] * 4 \
        + [Resource.WHEAT] * 4 + [Resource.ORE] * 3
    NUMBERS = [
        2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12
    ]
    # Ports are defined per outer side (6 sides). Each tuple is (position along side, resource or None for 3:1)
    # This distribution yields 9 ports total across the ring.
    PORTS = [
        [(0, None), (2, Resource.WOOL)],          # Side 0
        [(1, None)],                               # Side 1
        [(0, None), (2, Resource.BRICK)],         # Side 2
        [(1, Resource.WOOD)],                      # Side 3
        [(0, None), (2, Resource.WHEAT)],         # Side 4
        [(1, Resource.ORE)],                       # Side 5
    ]

    adj_lists_set = False

    def __init__(self, seed=None):
        #randomly initialize tile and number lists
        self.seed = seed

        self.generate_board()
        self.build_dicts()
        self.build_adj_lists()
        
    #randomly generate a new board
    def generate_board(self):
        np.random.seed(self.seed)
        resources = np.array(Board.RESOURCES)
        numbers = np.array(Board.NUMBERS)
        port_data = copy(Board.PORTS)

        np.random.shuffle(resources)
        np.random.shuffle(numbers)
        np.random.shuffle(port_data)

        desert_idx = np.random.randint(19)
        resources = np.insert(resources, desert_idx, Resource.DESERT)
        # Insert robber placeholder number for the desert tile
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
        
        Board.adj_lists_set = True

        
    def place_structure(self, coords, player, value, starting=False):
        node: Node = self.node_dict.get(Board.coords_hash(coords))
        if node is None:
            return False
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
        node.place_structure(player, value)
        for adj_idx in Board.node_node_list[node.index]:
            self.nodes[adj_idx].available = False
        node.available = False
        return True
    
    def place_road(self, coords, player):
        edge: Edge = self.edge_dict.get(Board.coords_hash(coords))
        if edge is None:
            return False
        if edge.player:
            return False
        #must place a road from an existing settlement or road,
        #road must not go through another players settlement
        
        # Determine the two nodes this edge connects
        node_indices = Board.edge_node_list[edge.index]
        connected_nodes: list[Node] = [self.nodes[i] for i in node_indices]
        
        # A node with an opponent settlement blocks connectivity through that node
        def node_blocked(n: Node) -> bool:
            return n.player is not None and n.player != player

        # Check if this road is connected to player's existing structure or road
        def connected_via_node(n: Node) -> bool:
            # Directly connected to own settlement/city
            if n.player == player:
                return True
            # Otherwise, check for adjacent player's road that shares this node
            for adj_edge_idx in Board.node_edge_list[n.index]:
                if adj_edge_idx == edge.index:
                    continue
                if self.edges[adj_edge_idx].player == player:
                    # Ensure we are not passing through an opponent settlement at this node
                    if not node_blocked(n):
                        return True
            return False

        # It is valid if there exists at least one node that is not blocked by opponent
        # and provides a connection (own building or own road)
        is_connected = False
        for n in connected_nodes:
            if node_blocked(n):
                continue
            if connected_via_node(n):
                is_connected = True
                break
        if not is_connected:
            return False

        edge.place_road(player)
        return True

    @staticmethod
    def coords_hash(coords):
        return coords[0] * 256 + coords[1]

    # Compute Longest Road length for a given player using DFS with node-visit constraints
    # This approximates official rules by preventing traversal through opponent settlements.
    # Complexity: O(E + V) per start due to memoization on (edge, blocked_node).
    def longest_road(self, player: str) -> int:
        # Build subgraph of player's edges and nodes
        owned_edge_indices = [e.index for e in self.edges if e.player == player]
        if not owned_edge_indices:
            return 0

        blocked_nodes = set(i for i, n in enumerate(self.nodes) if n.player is not None and n.player != player)

        # adjacency of edges via shared nodes, respecting blocked nodes
        edge_to_neighbors: dict[int, list[int]] = {}
        for ei in owned_edge_indices:
            neighbors = []
            for node_idx in Board.edge_node_list[ei]:
                if node_idx in blocked_nodes:
                    continue
                for adj_edge_idx in Board.node_edge_list[node_idx]:
                    if adj_edge_idx == ei:
                        continue
                    if self.edges[adj_edge_idx].player == player:
                        neighbors.append(adj_edge_idx)
            edge_to_neighbors[ei] = neighbors

        # DFS from each edge, tracking visited edges to avoid reuse
        best = 1
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def dfs(current_edge: int, visited_frozenset: frozenset[int]) -> int:
            length = 1
            visited = set(visited_frozenset)
            for nxt in edge_to_neighbors.get(current_edge, []):
                if nxt in visited:
                    continue
                new_visited = frozenset(visited | {nxt})
                length = max(length, 1 + dfs(nxt, new_visited))
            return length

        for start in owned_edge_indices:
            best = max(best, dfs(start, frozenset({start})))

        return best

class ActionType(Enum):
    structure = 0
    road = 1
    play_dev = 2
    buy_dev = 3
    roll = 4

    trade = 5

class GameAction:
    def __init__(self, type: ActionType):
        self.type = type

class StructureAction(GameAction):
    def __init__(self, coords, value):
        super().__init__(ActionType.structure)
        self.coords = coords
        self.value = value

class RoadAction(GameAction):
    def __init__(self, coords):
        super().__init__(ActionType.road)
        self.coords = coords

class DevType(Enum):
    knight = 0
    monopoly = 1
    road_build = 2
    invention = 3

    victory_point = 4

class PlayDevAction(GameAction):
    def __init__(self, dev_type: DevType):
        super().__init__(ActionType.play_dev)
        self.dev_type = dev_type

class BuyDevAction(GameAction):
    def __init__(self):
        super().__init__(ActionType.buy_dev)

class RollAction(GameAction):
    def __init__(self):
        super().__init__(ActionType.roll)


class Game:
    def __init__(self, players: list[str], seed=None):
        self.players = players
        self.seed = seed

        self.board = Board(seed=seed)
        self.cur_player = self.players[0]
        self.cur_player_idx = 0
        #start, prod, or action
        self.step_fn = self.step_start

        self.action_queue = deque([ActionType.structure, ActionType.road] * len(players))

        # turn state
        self.has_rolled = False
        self.actions_log: list[tuple] = []
        self.move_robber_pending = False

        self.bank_trade_rates = dict()
        for player in players:
            self.bank_trade_rates[player] = dict()
            for resource in Resource:
                self.bank_trade_rates[player][resource] = 4

        # player resources (exclude DESERT)
        self.player_resources: dict[str, dict[Resource, int]] = {
            p: {r: 0 for r in Resource if r != Resource.DESERT} for p in players
        }

        # piece inventory per player
        self.player_pieces: dict[str, dict[str, int]] = {
            p: {"roads": 15, "settlements": 5, "cities": 4} for p in players
        }

        # dev cards per player and deck state (to be initialized by API layer)
        self.player_devs_in_hand: dict[str, dict[str, int]] = {
            p: {
                "KNIGHT": 0,
                "MONOPOLY": 0,
                "YEAR_OF_PLENTY": 0,
                "ROAD_BUILDING": 0,
                "VICTORY_POINT": 0,
            }
            for p in players
        }
        self.player_devs_bought_this_turn: dict[str, dict[str, int]] = {
            p: {k: 0 for k in [
                "KNIGHT","MONOPOLY","YEAR_OF_PLENTY","ROAD_BUILDING","VICTORY_POINT"
            ]} for p in players
        }
        self.free_roads_remaining: dict[str, int] = {p: 0 for p in players}
        self.knights_played: dict[str, int] = {p: 0 for p in players}
        self.largest_army_owner: str | None = None
        self.longest_road_owner: str | None = None

        # robber starts on desert tile
        desert_tiles = [t for t in self.board.tiles if t.resource == Resource.DESERT]
        self.robber_coords = desert_tiles[0].coords if desert_tiles else self.board.tiles[0].coords
        
    
    def step(self, *args):
        # Forward the action to current step function
        return self.step_fn(*args)

    def step_start(self, action: GameAction):
        if action.type != self.action_queue[0]:
            #invalid action, returns false
            return False
        if action.type == ActionType.structure:
            if action.value != 1:
                return False
            ok = self.place_structure(action, starting=True)
            if not ok:
                return False
            # In initial phase, same player places a road after settlement
            self.action_queue.popleft()
            return True
        if action.type == ActionType.road:
            ok = self.place_road(action)
            if not ok:
                return False
            self.action_queue.popleft()
            self.advance_player()
            return True
        
        #success

    def place_structure(self, action: StructureAction, starting=False):
        r = self.board.place_structure(action.coords, self.cur_player, action.value, starting=starting)
        if not r:
            return False
        port: Port = self.board.node_port_dict.get(Board.coords_hash(action.coords), None)
        if port is not None:
            if port.resource is None:
                for res in Resource:
                    self.bank_trade_rates[self.cur_player][res] = min(3, self.bank_trade_rates[self.cur_player][res])
            else:
                self.bank_trade_rates[self.cur_player][port.resource] = 2
        return True
    
    def place_road(self, action: RoadAction):
        r = self.board.place_road(action.coords, self.cur_player)
        if not r:
            return False
        return True
                
    def advance_player(self):
        self.cur_player_idx += 1
        self.cur_player_idx %= len(self.players)
        self.cur_player = self.players[self.cur_player_idx]
        self.has_rolled = False
        self.move_robber_pending = False