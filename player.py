from globals import *
from copy import copy


class Player:
    def __init__(self, name):
        self.name = name
        
        self.bank_trade_rates = dict()
        self.resources: dict[Resource, int] = dict()
        for resource in Resource:
            self.bank_trade_rates[resource] = 4
            self.resources[resource] = 0

        self.resources_gen = dict()
        self.resources_block = dict()
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
            