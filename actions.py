from globals import DevType, Resource
from player import Player
from enum import Enum

class ActionType(Enum):
    end_turn = 'end_turn'
    settlement = 'settlement'
    city = 'city'
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
    discard = 'discard'

class Action:
    def __init__(self, type: ActionType):
        self.type = type

class SettlementAction(Action):
    def __init__(self, node_idx):
        super().__init__(ActionType.settlement)
        self.node_idx = node_idx

class CityAction(Action):
    def __init__(self, node_idx):
        super().__init__(ActionType.city)
        self.node_idx = node_idx

class RoadAction(Action):
    def __init__(self, edge_idx):
        super().__init__(ActionType.road)
        self.edge_idx = edge_idx

class PlayDevAction(Action):
    def __init__(self, dev_type: DevType):
        super().__init__(ActionType.play_dev)
        self.dev_type = DevType(dev_type)

class BuyDevAction(Action):
    def __init__(self):
        super().__init__(ActionType.buy_dev)

class RollAction(Action):
    def __init__(self):
        super().__init__(ActionType.roll)

class BankTradeAction(Action):
    def __init__(self, trade_in: dict[Resource, int], trade_for: dict[Resource, int]):
        super().__init__(ActionType.bank_trade)
        self.trade_in = trade_in
        self.trade_for = trade_for

class PlayerTradeAction(Action):
    def __init__(self, trade_in: dict[Resource, int], trade_for: dict[Resource, int]):
        super().__init__(ActionType.player_trade)
        self.trade_in = trade_in
        self.trade_for = trade_for

class MoveRobberAction(Action):
    def __init__(self, tile_idx):
        super().__init__(ActionType.move_robber)
        self.tile_idx = tile_idx

class StealAction(Action):
    def __init__(self, player: Player):
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
    
class DiscardAction(Action):
    def __init__(self, resources: dict[Resource, int]):
        super().__init__(ActionType.discard)
        self.resources = resources

class EndTurnAction(Action):
    def __init__(self):
        super().__init__(ActionType.end_turn)

ACTION_TYPES_DICT = {
    ActionType.end_turn: EndTurnAction,
    ActionType.settlement: SettlementAction,
    ActionType.city: CityAction,
    ActionType.road: RoadAction,
    ActionType.play_dev: PlayDevAction,
    ActionType.buy_dev: BuyDevAction,
    ActionType.roll: RollAction,
    ActionType.bank_trade: BankTradeAction,
    ActionType.player_trade: PlayerTradeAction,
    ActionType.move_robber: MoveRobberAction,
    ActionType.steal: StealAction,
    ActionType.monopoly: MonopolyAction,
    ActionType.invention: InventionAction,
    ActionType.discard: DiscardAction
}

ACTION_TYPES = list(ACTION_TYPES_DICT.keys())
ACTION_CLASSES = list(ACTION_TYPES_DICT.values())

def create_action(type: str | ActionType, kwargs: dict[str]):
    try:
        action_class = ACTION_TYPES_DICT[ActionType(type)]
        return action_class(**kwargs)
    except Exception as e:
        return None