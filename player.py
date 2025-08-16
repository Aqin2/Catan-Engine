from globals import *
from catan import DevType
from copy import copy


class Player:
    def __init__(self, name):
        self.name = name
        
        self.bank_trade_rates = dict()
        self.resources = dict()
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

        self.dev_cards = dict()
        self.dev_cards_cur_turn = dict()
        for dev_type in DevType:
            self.dev_cards[dev_type] = 0
            self.dev_cards_cur_turn[dev_type] = 0
        

        self.victory_points = 0
        self.longest_road_len = 0
        self.num_knights_played = 0
        self.has_longest_road = False
        self.has_largest_army = False

    def gen_resources(self, roll_n):
        resource_gain = self.resources_gen[roll_n]
        resource_block = self.resources_block[roll_n]
        for resource in Resource:
            if resource != Resource.DESERT:
                self.resources[resource] += resource_gain[resource] - resource_block[resource]

    def reset_resource_block(self):
        for roll in range(2, 13):
            if roll == 7:
                continue
            for resource in Resource:
                if resource != Resource.DESERT:
                    self.resources_block[roll][resource] = 0
            