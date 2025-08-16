from enum import Enum
from collections import deque
from copy import copy

from globals import *
from entities import *
from actions import *
from board import Board
from player import Player

class Game:
    roll_p = np.convolve(np.full((6,), 1 / 6), np.full((6,), 1 / 6))
    SETTLEMENT_COST = {
        Resource.BRICK: 1,
        Resource.WOOD: 1,
        Resource.WOOL: 1,
        Resource.WHEAT: 1
    }
    CITY_COST = {
        Resource.WHEAT: 2,
        Resource.ORE: 3,
    }
    ROAD_COST = {
        Resource.BRICK: 1,
        Resource.WOOD: 1
    }
    DEV_CARD_COST = {
        Resource.WOOL: 1,
        Resource.WHEAT: 1,
        Resource.ORE: 1
    }
    DEV_CARDS = [DevType.knight] * 14 + [DevType.victory_point] * 5 + [DevType.monopoly] * 2 + \
        [DevType.road_build] * 2 + [DevType.monopoly] * 2


    def __init__(self, player_names: list[str], seed=None):
        self.random = np.random.default_rng(seed=seed)
        self.player_names = player_names
        self.seed = seed

        self.board = Board(seed=seed)
        self.cur_player_name = self.player_names[0]
        self.cur_player_idx = 0
        #start, prod, or action
        self.step_fn = self.step_start

        self.action_queue = deque([ActionType.structure, ActionType.road] * len(player_names))
    
        #player info
        self.player_data: dict[str, Player] = dict()
        for player in self.player_names:
            self.player_data[player] = Player(player)


        #current player info for current turn
        self.road_dev_count = 0 #how many free roads remaining if has played road building dev card
        self.has_played_dev = False
        self.has_rolled = False

        self.dev_cards = copy(Game.DEV_CARDS)
        self.random.shuffle(self.dev_cards)
        
    
    def step(self, *args):
        res = self.step_fn(args)

    def step_start(self, action: Action):
        if action.type != self.action_queue[0]:
            #invalid action, returns false
            return False
        if action.type == ActionType.structure:
            if action.value != 1:
                return False
            res = self.place_structure(self, action, starting=True)
            if res:
                self.action_queue.popleft()
            return res
        if action.type == ActionType.road:
            res = self.place_road(self, action, starting=True)
            if res:
                self.action_queue.popleft()
                self.advance_player()
            return res
        
        return False
    
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
        
        if r and use_queue:
            self.action_queue.popleft()
        return r


    def place_structure(self, action: StructureAction, starting=False):
        if (not starting) and (not self.has_rolled):
            return False
        r = self.board.place_structure(action.coords, self.cur_player_data, action.value, starting=starting)
        if not r:
            return False
    
        if action.value == 1:
            if self.cur_player_data.rem_settlements <= 0:
                return False
            if not starting:
                if not self.pay_cost(Game.SETTLEMENT_COST):
                    return False
            self.cur_player_data.rem_settlements -= 1

        elif action.value == 2:
            if self.cur_player_data.rem_cities <= 0:
                return False
            if not self.pay_cost(Game.CITY_COST):
                return False
            self.cur_player_data.rem_cities -= 1


        port: Port = self.board.node_port_dict.get(Board.coords_hash(action.coords), None)
        if port is not None:
            if port.resource is None:
                for res in Resource:
                    self.cur_player_data.bank_trade_rates[res] = min(3, self.cur_player_data.bank_trade_rates[res])
            else:
                self.cur_player_data.bank_trade_rates[port.resource] = 2

        return True
    
    def place_road(self, action: RoadAction, starting=False):
        if (not starting) and (not self.has_rolled):
            return False
        r = self.board.place_road(action.coords, self.cur_player_data)
        if not r:
            return False
        
        if self.road_dev_count == 0:
            if not self.pay_cost(Game.ROAD_COST):
                return False
        
        self.cur_player_data.rem_roads -= 1
        if self.road_dev_count > 0:
            self.road_dev_count -= 1

        #TODO: check longest road

        return True

    def play_dev(self, action: PlayDevAction):
        if self.has_played_dev:
            return False
        dev_type = action.dev_type
        #cant play dev cards on the turn they were bought
        if self.cur_player_data.dev_cards[dev_type] - self.cur_player_data.dev_cards_cur_turn[dev_type] <= 0:
            return False
        #TODO: implement different types of actions

        match action.dev_type:
            case DevType.knight:
                self.action_queue.append(ActionType.move_robber)

        return True
        
        
    def buy_dev(self, action: BuyDevAction):
        if not self.has_rolled:
            return False
        if len(self.dev_cards) <= 0:
            return False
        if not self.pay_cost(Game.DEV_CARD_COST):
            return False
        dev_card = self.dev_cards.pop()
        self.cur_player_data.dev_cards[dev_card] += 1
        self.cur_player_data.dev_cards_cur_turn[dev_card] += 1
        return True
        
        
    def roll(self, action: RollAction):
        if self.has_rolled:
            return False
        
        roll_n = self.get_roll_n()

        if roll_n == 7:
            self.action_queue.append(ActionType.move_robber)
            pass
        else:
            for player in self.player_data.values():
                player.gen_resources()
        return True
            
    def move_robber(self, action: MoveRobberAction):
        r = self.board.move_robber(action.tile_coords)
        if not r:
            return False
        
        #TODO: only add steal action if more than 1 player has at least 1 resource next to robber tile
        self.action_queue.append(ActionType.steal)
        
        for player in self.player_data.values():
            player.reset_resource_block()
    
        robber_tile = self.board.robber_tile
        if robber_tile.resource == Resource.DESERT:
            #nothing blocked if robber is on desert
            return True

        for node_idx in Board.tile_node_list[robber_tile.index]:
            node = self.board.nodes[node_idx]
            if node.player:
                node.player.resources_block[robber_tile.number][robber_tile.resource] += node.value
        
        return True
    
    def steal(self, action: StealAction):
        #TODO: implement this

        #check if player is not self and has a settlement/city next to the robber tile
        #steal a random resource (use resource amounts as weights)

        #pirate software tribute
        # match gl_arr[118974][21485]:
        #     case 1:
        #         what_the.johio_ohn()
        #     case 2:
        #         what_the.johio_ohn()
        #     case 3:
        #         what_the.johio_ohn()
        #     case 4:
        #         what_the.johio_ohn()
        #     case _:
        #         what_the.johio_ohn()


        pass


    def bank_trade(self, action: RollAction):
        if not self.has_rolled:
            return False
                
    def pay_cost(self, cost: dict[Resource, int]):
        for resource in Resource:
            if resource != Resource.DESERT:
                if self.cur_player_data[resource] < cost[resource]:
                    return False
                
        for resource in Resource:
            if resource != Resource.DESERT:
                self.cur_player_data[resource] -= cost[resource]

        return True
    
    def advance_player(self):
        for dev_type in DevType:
            self.cur_player_data.dev_cards_cur_turn[dev_type] = 0

        self.cur_player_idx += 1
        self.cur_player_idx %= len(self.player_names)
        self.cur_player_name = self.player_names[self.cur_player_idx]
        self.cur_player_data = self.player_data[self.cur_player_idx]

    def get_roll_n(self):
        return self.random.choice([i for i in range(2, 13)], p=Game.roll_p)