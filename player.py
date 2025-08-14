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

        self.resource_gen = dict()
        for roll in range(2, 13):
            if roll == 7:
                continue
            self.resource_gen[roll] = copy(self.resources)
        
        self.rem_settlements = 5
        self.rem_cities = 4
        self.rem_roads = 15

        self.dev_cards = dict()
        for dev_type in DevType:
            self.dev_cards[dev_type] = 0

        self.victory_points = 0
        self.has_longest_road = False
        self.has_largest_army = False

        
            