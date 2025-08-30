from globals import DevType, Resource
from enum import Enum

class ActionType(Enum):
    end_turn = 'end_turn'
    structure = 'structure'
    road = 'road'
    play_dev = 'play_dev'
    buy_dev = 'buy_dev'
    roll = 'roll'
    bank_trade = 'bank_trade'
    player_trade = 'player_trade' #not implemented
    move_robber = 'move_robber'
    steal = 'steal'
    monopoly = 'monopoly'
    invention = 'invention'

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

ACTION_TYPES = {
    ActionType.end_turn: EndTurnAction,
    ActionType.structure: StructureAction,
    ActionType.road: RoadAction,
    ActionType.play_dev: PlayDevAction,
    ActionType.buy_dev: BuyDevAction,
    ActionType.roll: RollAction,
    ActionType.bank_trade: BankTradeAction,
    #ActionType.player_trade: PlayerTradeAction,
    ActionType.move_robber: MoveRobberAction,
    ActionType.steal: StealAction,
    ActionType.monopoly: MonopolyAction,
    ActionType.invention: InventionAction
}

def create_action(type: str | ActionType, kwargs: dict[str]):
    try:
        action_class = ACTION_TYPES[ActionType(type)]
        return action_class(**kwargs)
    except:
        return None