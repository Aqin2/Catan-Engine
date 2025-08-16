from globals import DevType, Resource
from enum import Enum

class ActionType(Enum):
    end_turn = 0
    structure = 1
    road = 2
    play_dev = 3
    buy_dev = 4
    roll = 5
    bank_trade = 6
    player_trade = 7 #not implemented
    move_robber = 8
    steal = 9
    monopoly = 10
    invention = 11

class Action:
    def __init__(self, type: ActionType):
        self.type = type

class StructureAction(Action):
    def __init__(self, coords, value):
        super().__init__(ActionType.structure)
        self.coords = coords
        self.value = value

class RoadAction(Action):
    def __init__(self, coords):
        super().__init__(ActionType.road)
        self.coords = coords

class PlayDevAction(Action):
    def __init__(self, dev_type: DevType):
        super().__init__(ActionType.play_dev)
        self.dev_type = dev_type

class BuyDevAction(Action):
    def __init__(self):
        super().__init__(ActionType.buy_dev)

class RollAction(Action):
    def __init__(self):
        super().__init__(ActionType.roll)

class BankTradeAction(Action):
    def __init__(self, trade_in, trade_for):
        super().__init__(ActionType.bank_trade)
        self.trade_in = trade_in
        self.trade_for = trade_for

class MoveRobberAction(Action):
    def __init__(self, tile_coords):
        super().__init__(ActionType.move_robber)
        self.tile_coords = tile_coords

class StealAction(Action):
    def __init__(self, player):
        super().__init__(ActionType.steal)
        self.player = player

class MonopolyAction(Action):
    def __init__(self, resource: Resource):
        super().__init__(ActionType.monopoly)
        self.resource = resource

class InventionAction(Action):
    def __init__(self, resources: dict[Resource, int]):
        super().__init__(ActionType.invention)
        self.resources = resources

class EndTurnAction(Action):
    def __init__(self):
        super().__init__(ActionType.end_turn)