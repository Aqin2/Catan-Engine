from enum import Enum
from collections import deque

from globals import *
from entities import *
from board import Board
from player import Player

class ActionType(Enum):
    end_turn = 0
    structure = 1
    road = 2
    play_dev = 3
    buy_dev = 4
    roll = 5

    bank_trade = 6

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

class BankTradeAction(GameAction):
    def __init__(self, trade_in, trade_for):
        super().__init__(ActionType.bank_trade)
        self.trade_in = trade_in
        self.trade_for = trade_for

class EndTurnAction(GameAction):
    def __init__(self):
        super().__init__(ActionType.end_turn)


class Game:
    roll_p = np.convolve(np.full((6,), 1 / 6), np.full((6,), 1 / 6))

    def __init__(self, player_names: list[str], seed=None):
        np.random.seed(seed)
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


        
        
    
    def step(self, *args):
        res = self.step_fn(args)

    def step_start(self, action: GameAction):
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
    
    def step_main(self, action: GameAction):
        if len(self.action_queue) == 0:
            match action.type:
                case ActionType.end_turn:
                    if self.has_rolled:
                        self.advance_player()
                        return True
                    else:
                        return False
                case ActionType.structure:
                    return self.place_structure(action)
                case ActionType.road:
                    return self.place_road(action)
                case ActionType.play_dev:
                    return self.play_dev(action)
                case ActionType.buy_dev:
                    return self.buy_dev(action)
                case ActionType.roll:
                    return self.roll(action)
                case ActionType.bank_trade:
                    return self.bank_trade(action)


    def place_structure(self, action: StructureAction, starting=False):
        if (not starting) and (not self.has_rolled):
            return False
        r = self.board.place_structure(action.coords, self.cur_player_data, action.value, starting=starting)
        if not r:
            return False
        
        if action.value == 1:
            self.cur_player_data.rem_settlements -= 1
        elif action.value == 2:
            self.cur_player_data.rem_cities -= 1
            self.cur_player_data.rem_settlements += 1 #not really necessary but more realistic

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
        
        self.cur_player_data.rem_roads -= 1

        #TODO: check longest road

        return True

    def play_dev(self, action: PlayDevAction):
        if self.has_played_dev:
            return False
        
    def buy_dev(self, action: BuyDevAction):
        if not self.has_rolled:
            return False
        
    def roll(self, action: RollAction):
        if self.has_rolled:
            return False
        
        roll_n = self.get_roll_n()

        if roll_n == 7:
            #TODO: queue up a move robber action
            pass
        else:
            for player in self.player_data.values():
                resource_gain = player.resource_gen[roll_n]
                for resource in Resource:
                    player.resources[resource] += resource_gain[resource]
        return True
            
    
    def bank_trade(self, action: RollAction):
        if not self.has_rolled:
            return False
                
    def advance_player(self):
        self.cur_player_idx += 1
        self.cur_player_idx %= len(self.player_names)
        self.cur_player_name = self.player_names[self.cur_player_idx]
        self.cur_player_data = self.player_data[self.cur_player_idx]

    def get_roll_n(self):
        return np.random.choice([i for i in range(2, 13)], p=Game.roll_p)