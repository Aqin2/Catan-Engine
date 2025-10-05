from globals import *
from copy import copy


class Player:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        
        self.bank_trade_rates = dict()
        self.resources: dict[Resource, int] = dict()
        for resource in Resource:
            self.bank_trade_rates[resource] = 4
            self.resources[resource] = 0

        self.resources_gen: dict[int, dict[Resource, int]] = dict()
        self.resources_block: dict[int, dict[Resource, int]] = dict()
        for roll in range(2, 13):
            if roll == 7:
                continue
            self.resources_gen[roll] = copy(self.resources)
            self.resources_block[roll] = copy(self.resources)
        
        self.rem_settlements = 5
        self.rem_cities = 4
        self.rem_roads = 15

        self.n_settlements = 0
        self.n_cities = 0

        self.dev_cards: dict[DevType, int] = dict()
        self.dev_cards_cur_turn = dict()
        for dev_type in DevType:
            self.dev_cards[dev_type] = 0
            self.dev_cards_cur_turn[dev_type] = 0

        self.victory_points = 0
        self.longest_road_len = 0
        self.num_knights_played = 0
        self.has_longest_road = False
        self.has_largest_army = False

        #speeds up longest road computation
        self.roads = []

    def reset_resource_block(self):
        for roll in range(2, 13):
            if roll == 7:
                continue
            for resource in Resource:
                self.resources_block[roll][resource] = 0
    
    def calculate_victory_points(self):
        victory_points = 0
        victory_points += self.n_settlements * 1
        victory_points += self.n_cities * 2
        victory_points += 2 if self.has_largest_army else 0
        victory_points += 2 if self.has_longest_road else 0
        victory_points += self.dev_cards[DevType.victory_point] * 1
        
        self.victory_points = victory_points

    def to_json_obj(self):
        return {
            'resources': {resource.value: count for resource, count in self.resources.items()},
            'dev_cards': {card.value: count for card, count in self.dev_cards.items()}
        }
    
    def get_obs(self, player_idx):
        obs = dict()

        obs['bank_trade_rates'] = np.zeros((5,), dtype=np.int32)
        for i, value in enumerate(self.bank_trade_rates.values()):
            obs['bank_trade_rates'][i] = value
        obs['resources'] = np.zeros((5,), dtype=np.int32)
        for i, value in enumerate(self.resources.values()):
            obs['resources'][i] = value
        obs['resources_gen'] = np.zeros((10, 5), dtype=np.int32)
        for i, values in enumerate(self.resources_gen.values()):
            for j, value in enumerate(values.values()):
                obs['resources_gen'][i][j] = value
        obs['resources_block'] = np.zeros((10, 5), dtype=np.int32)
        for i, values in enumerate(self.resources_block.values()):
            for j, value in enumerate(values.values()):
                obs['resources_block'][i][j] = value
        obs['rem_settlements'] = self.rem_settlements
        obs['rem_cities'] = self.rem_cities
        obs['rem_roads'] = self.rem_roads
        obs['longest_road_len'] = self.longest_road_len
        obs['num_knights_played'] = self.num_knights_played
        obs['has_longest_road'] = 1 if self.has_longest_road else 0
        obs['has_largest_army'] = 1 if self.has_largest_army else 0

        if self.index == player_idx:
            obs['dev_cards'] = np.zeros((5), dtype=np.int32)
            for i, value in enumerate(self.dev_cards.values()):
                obs['dev_cards'][i] = value
            obs['dev_cards_cur_turn'] = np.zeros((5), dtype=np.int32)
            for i, value in enumerate(self.dev_cards_cur_turn.values()):
                obs['dev_cards_cur_turn'][i] = value
            obs['victory_points'] = self.victory_points
        else:
            obs['num_dev_cards'] = sum(self.dev_cards.values())
            obs['victory_points'] = self.victory_points - self.dev_cards[DevType.victory_point]
        
        return obs