from enum import Enum
from collections import deque
from copy import copy
import json

from globals import *
from entities import *
from actions import *
from board import Board
from player import Player

class Game:
    roll_p = np.convolve(np.full((6,), 1 / 6), np.full((6,), 1 / 6))
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
    DEV_CARD_COST = {
        Resource.wool: 1,
        Resource.wheat: 1,
        Resource.ore: 1
    }
    DEV_CARDS = [DevType.knight] * 14 + [DevType.victory_point] * 5 + [DevType.monopoly] * 2 + \
        [DevType.road_build] * 2 + [DevType.monopoly] * 2


    def __init__(self, player_names: list[str], seed=None, victory_callback=None):
        self.random = np.random.default_rng(seed=seed)
        self.player_names = player_names
        self.seed = seed

        self.board = Board(seed=seed)
       
        #start, prod, or action
        self.step_fn = self.step_start
        self.action_queue = deque([ActionType.structure, ActionType.road] * len(self.player_names) * 2)

        #player info
        self.players: dict[str, Player] = dict()
        for player in self.player_names:
            self.players[player] = Player(player)
        self.cur_player = self.players[self.player_names[0]]
        self.cur_player_idx = 0

        #current player info for current turn
        self.road_dev_count = 0 #how many free roads remaining if has played road building dev card
        self.has_played_dev = False
        self.has_rolled = False
        self.played_knight = False

        #longest road, largest army
        self.p_longest_road: Player = None
        self.p_largest_army: Player = None

        #game resources and dev cards
        self.resources = dict()
        for resource in Resource:
            self.resources[resource] = 19

        self.dev_cards = copy(Game.DEV_CARDS)
        self.random.shuffle(self.dev_cards)

        self.victory_callback = victory_callback    
    
    def step(self, action: Action):
        r = self.step_fn(action)
        return r

    def step_start(self, action: Action):
        if action.type != self.action_queue[0]:
            #invalid action, returns false
            return False
        r = False
        if action.type == ActionType.structure:
            if action.value != 1:
                return False
            r = self.place_structure(self, action, starting=True)
            if r:
                self.action_queue.popleft()

        if action.type == ActionType.road:
            r = self.place_road(self, action, starting=True)
            if r:
                self.action_queue.popleft()
                if len(self.action_queue) == 0:
                    self.step_fn = self.step_main
                elif len(self.action_queue) <= len(self.players) * 2:
                    #exactly halfway, reverse order
                    self.advance_player(increment=-1)
                else:
                    self.advance_player()

        return r
    
    def step_main(self, action: Action):
        use_queue = len(self.action_queue) > 0

        cur_action = self.action_queue[0] if use_queue else action
        if action.type != cur_action.type:
            return False

        r = False
        
        match cur_action.type:
            case ActionType.end_turn:
                if self.has_rolled:
                    self.advance_player()
                    r = True
                else:
                    r = False
            case ActionType.structure:
                r = self.place_structure(action)
            case ActionType.road:
                r = self.place_road(action)
            case ActionType.play_dev:
                r = self.play_dev(action)
            case ActionType.buy_dev:
                r = self.buy_dev(action)
            case ActionType.roll:
                r = self.roll(action)
            case ActionType.bank_trade:
                r = self.bank_trade(action)
            case ActionType.move_robber:
                r = self.move_robber(action)
            case ActionType.steal:
                r = self.steal(action)
            case ActionType.monopoly:
                r = self.monopoly(action)
            case ActionType.invention:
                r = self.invention(action)
        
        if r and use_queue:
            self.action_queue.popleft()
        return r


    def place_structure(self, action: StructureAction, starting=False):
        if (not starting) and (not self.has_rolled):
            return False
        r = self.board.place_structure(action.coords, self.cur_player, action.value, starting=starting)
        if not r:
            return False
    
        if action.value == 1:
            if self.cur_player.rem_settlements <= 0:
                return False
            if not starting:
                if not self.pay_cost(Game.SETTLEMENT_COST):
                    return False
            self.cur_player.rem_settlements -= 1
            self.cur_player.n_settlements += 1

        elif action.value == 2:
            if self.cur_player.rem_cities <= 0:
                return False
            if not self.pay_cost(Game.CITY_COST):
                return False
            self.cur_player.rem_cities -= 1
            self.cur_player.n_settlements -= 1
            self.cur_player.n_cities += 1

        port: Port = self.board.node_port_dict.get(Board.coords_hash(action.coords), None)
        if port is not None:
            if port.resource is None:
                for res in Resource:
                    self.cur_player.bank_trade_rates[res] = min(3, self.cur_player.bank_trade_rates[res])
            else:
                self.cur_player.bank_trade_rates[port.resource] = 2

        self.check_victory()

        return True
    
    def place_road(self, action: RoadAction, starting=False):
        if (not starting) and (not self.has_rolled):
            return False
        
        if self.road_dev_count == 0:
            if not self.pay_cost(Game.ROAD_COST):
                return False
            
        r = self.board.place_road(action.coords, self.cur_player)
        if not r:
            return False
        
        self.cur_player.rem_roads -= 1
        if self.road_dev_count > 0:
            self.road_dev_count -= 1

        #TODO: check longest road
        return True

    def play_dev(self, action: PlayDevAction):
        if self.has_played_dev:
            return False
        dev_type = action.dev_type
        #cant play dev cards on the turn they were bought
        if self.cur_player.dev_cards[dev_type] - self.cur_player.dev_cards_cur_turn[dev_type] <= 0:
            return False

        match action.dev_type:
            case DevType.knight:
                self.action_queue.append(ActionType.move_robber)
                self.played_knight = True
            case DevType.monopoly:
                self.action_queue.append(ActionType.monopoly)
            case DevType.road_build:
                self.road_dev_count = 2

                self.action_queue.append(ActionType.road)
                self.action_queue.append(ActionType.road)
            case DevType.invention:
                self.action_queue.append(ActionType.invention)
            case _:
                #cant play victory point dev card
                return False
            
        self.has_played_dev = True
        return True
        
    def buy_dev(self, action: BuyDevAction):
        if not self.has_rolled:
            return False
        if len(self.dev_cards) <= 0:
            return False
        if not self.pay_cost(Game.DEV_CARD_COST):
            return False
        dev_card = self.dev_cards.pop()
        self.cur_player.dev_cards[dev_card] += 1
        self.cur_player.dev_cards_cur_turn[dev_card] += 1
        self.check_victory()
        return True
        
    def roll(self, action: RollAction):
        if self.has_rolled:
            return False
        
        self.has_rolled = True
        roll_n = self.get_roll_n()

        if roll_n == 7:
            self.action_queue.append(ActionType.move_robber)
            pass
        else:
            self.gen_resources(roll_n)
            pass
        return True
    
    def gen_resources(self, roll_n):
        total_gen = dict()
        gen_players: dict[str, list[Player]] = dict()
        for resource in Resource:
            total_gen[resource] = 0
            gen_players = []

        for player in self.players.values():
            for resource in Resource:
                gen = player.resources_gen[roll_n][resource] - player.resources_block[roll_n][resource]
                if gen > 0:
                    total_gen[resource] += gen
                    gen_players[resource].append(player)

        for resource in Resource:
            if self.resources[resource] < total_gen[resource]:
                #if less than required resources, only give the resources if only one player can generate them
                if len(gen_players[resource]) == 1:
                    player = gen_players[resource][0]
                    #give all that remains
                    player.resources[resource] += self.resources[resource]
                    self.resources[resource] = 0
            else:
                for player in gen_players[resource]:
                    gen = player.resources_gen[roll_n][resource] - player.resources_block[roll_n][resource]
                    player.resources[resource] += gen
                    self.resources[resource] -= gen

            
    def move_robber(self, action: MoveRobberAction):
        r = self.board.move_robber(action.tile_coords)
        if not r:
            return False
        
        robber_tile = self.board.robber_tile
        n_steal = 0
        for node_idx in Board.tile_node_list[robber_tile.index]:
            node = self.board.nodes[node_idx]
            #must have a player and must not be self
            if node.player and node.player != self.cur_player:
                #and must have at least 1 resource
                if np.any(node.player.resources.values()):
                    n_steal += 1

        #only add steal action if more than 1 eligible player to steal from
        if n_steal > 1:
            self.action_queue.append(ActionType.steal)

        #recalculate blocked resources
        for player in self.players.values():
            player.reset_resource_block()
        
        if robber_tile.resource is None:
            #nothing blocked if robber is on desert
            return True

        for node_idx in Board.tile_node_list[robber_tile.index]:
            node = self.board.nodes[node_idx]
            if node.player:
                node.player.resources_block[robber_tile.number][robber_tile.resource] += node.value
        
        if self.played_knight:
            self.cur_player.num_knights_played += 1


        return True
    
    def steal(self, action: StealAction):
        if action.player is None:
            return False
        #cant steal from yourself
        if action.player == self.cur_player:
            return False
        
        robber_tile = self.board.robber_tile
        for node_idx in Board.tile_node_list[robber_tile.index]:
            node = self.board.nodes[node_idx]
            if node.player == action.player:
                if np.any(node.player.resources.values()):
                    resource_arr = np.array(node.player.resources.values())
                    total = np.sum(resource_arr)

                    stolen = self.random.choice(node.player.resources.keys(), p=resource_arr / total)

                    node.player.resources[stolen] -= 1
                    self.cur_player.resources[stolen] += 1

                    return True
                else:
                    #player has no resources to steal from
                    return False
        
        #player has no settlement/city on robber tile
        return False

    def monopoly(self, action: MonopolyAction):
        if self.resources[action.resource] == 19:
            #no one has wanted resource
            #might still be allowed if player is dumb
            return False
        
        for player in self.players.values():
            if player != self.cur_player:
                self.cur_player.resources[action.resource] += player.resources[action.resource]
                player.resources[action.resource] = 0

        return True
    
    def invention(self, action: InventionAction):
        if np.sum(action.resources.values()) != 2:
            return False

        for resource in Resource:
            if action.resources[resource] > self.resources[resource]:
                #not enough resources
                return False
        
        for resource in Resource:
            self.cur_player.resources[resource] += action.resources[resource]
            self.resources[resource] -= action.resources[resource]
        
        return True


    def bank_trade(self, action: RollAction):
        if not self.has_rolled:
            return False
                
    def pay_cost(self, cost: dict[Resource, int]):
        for resource in Resource:
            if self.cur_player[resource] < cost[resource]:
                return False
                
        for resource in Resource:
            self.cur_player[resource] -= cost[resource]
            self.resources[resource] += cost[resource]

        return True
    
    def check_largest_army(self):
        new_largest_army = None
        for player in self.players.values():
            if player.num_knights_played < 3:
                continue

            if new_largest_army is None:
                new_largest_army = player
            elif new_largest_army.num_knights_played < player.num_knights_played:
                new_largest_army = player
        
        if new_largest_army.num_knights_played > self.p_largest_army.num_knights_played:
            self.p_largest_army = new_largest_army
            self.check_victory()
            

    def check_victory(self):
        for player in self.players.values():
            player.calculate_victory_points()
            if player.victory_points >= 10:
                self.victory_callback()
                return True
        return False
    
    def advance_player(self, increment=1):
        self.road_dev_count = 0
        self.has_rolled = False
        self.has_played_dev = False
        self.played_knight = False
        for dev_type in DevType:
            self.cur_player.dev_cards_cur_turn[dev_type] = 0

        self.cur_player_idx += increment
        self.cur_player_idx %= len(self.players)
        self.cur_player = self.players[self.cur_player_idx]

    def get_roll_n(self):
        return self.random.choice([i for i in range(2, 13)], p=Game.roll_p)
    
    '''
    json obj format:
    {
        cur_player: string //which player's turn it is
        expected_action: string | null, //the next action expected or null for no specific action
        board: Board, //(see board.py)

        //TODO: implement this
        players: {
            [player_name]: {
                
            }
        }
    }
    '''
    def to_json_obj(self):
        obj = dict()
        obj['cur_player'] = self.cur_player.name
        obj['expeted_action'] = self.action_queue[0].value if len(self.action_queue) > 0 else None
        obj['board'] = self.board.to_json_obj()

        return obj