from pettingzoo import AECEnv
from gymnasium.spaces import *
from gymnasium.spaces.utils import flatten_space, flatten, unflatten
from game import Game
import numpy as np
from actions import *
from globals import RESOURCE_TYPES_LIST, DEV_TYPES_LIST

class CatanEnv(AECEnv):
    metadata = {
        'name': 'catan_env_v0'
    }

    def __init__(self, player_names: list[str]):
        self.possible_agents = player_names
        self.agents = self.possible_agents


        #every obs with a value for each player has the order
        #0 = current player
        #1 = next player
        #2 = next next player
        #...

        #TODO: pettingzoo hates dict obs spaces
        #write a function that takes the dict down here
        #and flattens into a single numpy array
        self._obs_space = Dict({
            'nodes': MultiDiscrete([[3] * self.num_agents] * 54),
            'edges': MultiBinary([72, self.num_agents]),
            'tile_types': MultiBinary([19, 6]),
            'tile_nums': MultiDiscrete([13] * 19),
            'robber_tile': MultiBinary(19),
            'player': Dict({
                'bank_trade_rates': MultiDiscrete([5] * 5),
                'resources': MultiDiscrete([20] * 5),
                'resources_gen': MultiDiscrete([[11] * 5] * 10),
                'resources_block': MultiDiscrete([[7] * 5] * 10),
                'rem_settlements': Discrete(6),
                'rem_cities': Discrete(5),
                'rem_roads': Discrete(16),
                'dev_cards': MultiDiscrete([15, 3, 3, 3, 6]),
                'dev_cards_cur_turn': MultiDiscrete([15, 3, 3, 3, 6]),
                'victory_points': Discrete(11),
                'longest_road_len': Discrete(16),
                'num_knights_played': Discrete(20), # technically infinite knights can be played but very unlikely for >= 20
                'has_longest_road': Discrete(2),
                'has_largest_army': Discrete(2)
            }),
            # each element in 'opponents' is a dict very similar to 'player', but no 'dev_cards' or 'dev_cards_cur_turn',
            # instead 'num_dev_cards' replaces both of them (can't see dev cards of other players)
            'opponents': Tuple([Dict({
                'bank_trade_rates': MultiDiscrete([5] * 5),
                'resources': MultiDiscrete([20] * 5),
                'resources_gen': MultiDiscrete([[11] * 5] * 10),
                'resources_block': MultiDiscrete([[7] * 5] * 10),
                'rem_settlements': Discrete(6),
                'rem_cities': Discrete(5),
                'rem_roads': Discrete(16),
                'num_dev_cards': Discrete(26), # <<< replaces 'dev_cards' and 'dev_cards_cur_turn'
                'victory_points': Discrete(11), # <<< victory points from dev cards not counted
                'longest_road_len': Discrete(16),
                'num_knights_played': Discrete(20),
                'has_longest_road': Discrete(2),
                'has_largest_army': Discrete(2)
            })] * (self.num_agents - 1))
        })
        self._flat_obs_space = flatten_space(self._obs_space)

        '''
        action space encoding: MultiDiscrete([14, 19, 72, 54, 4, (n players), 5] + [20] * 10)
        [0]:
        action type
            0: end turn
            1: structure
            2: road
            ...
            12: discard
        [1]:
        tile id
        [2]:
        edge id
        [3]:
        node id (settlement)
        [4]:
        node id (city)
        [5]:
        dev card 
        [6]:
        player to steal from
        [7]:
        resource to monopolize
        [8 : 13]:
        resources being received
        used for trades, invention dev card
        [13  : 18]:
        resources being spent
        used for trades, discarding
        '''
        self._act_space = MultiDiscrete([14, 19, 72, 54, 54, 4, self.num_agents, 5] + [20] * 10)

    def seed(self, seed=None):
        self.game_seed = seed

    def reset(self, seed = None, options = None): 
        self.seed(seed)
        
        self.game = Game(player_names=self.agents, seed=self.game_seed)
        self.agent_selection = self.agents[self.game.cur_player_idx]
        self.terminations = {name: False for name in self.agents}
        self.truncations = {name: False for name in self.agents}
        self.infos = {name: {} for name in self.agents}
        self.rewards = {name: 0 for name in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}

    def step(self, action):
        self.game.step(self.get_action(action))
        
    def observe(self, agent):
        return flatten(self._obs_space, self.game.get_obs(self.agents.index(agent)))

    def observation_space(self, agent):
        return self._flat_obs_space
    
    
    def action_space(self, agent):
        return self._act_space


    #TODO: this function is hideous
    #clean it up
    def get_action(self, action: np.ndarray):
        action_class = ACTION_CLASSES[action[0]]
        action_type = ACTION_TYPES[action[0]]

        match action_type:
            case ActionType.end_turn | ActionType.buy_dev | ActionType.roll:
                return action_class()
            case ActionType.settlement:
                return action_class(action[3])
            case ActionType.city:
                return action_class(action[4])
            case ActionType.road:
                return action_class(action[2])
            case ActionType.play_dev:
                type = DEV_TYPES_LIST[action[5]]
                return action_class(type)
            case ActionType.bank_trade | ActionType.player_trade:
                trade_in = dict(zip(RESOURCE_TYPES_LIST, action[13:]))
                trade_for = dict(zip(RESOURCE_TYPES_LIST, action[8:13]))
                return action_class(trade_in, trade_for)
            case ActionType.move_robber:
                return action_class(action[1])
            case ActionType.steal:
                player = self.possible_agents[action[6]]
                return action_class(player)
            case ActionType.monopoly:
                resource = RESOURCE_TYPES_LIST[action[7]]
                return action_class(resource)
            case ActionType.invention:
                trade_for = dict(zip(RESOURCE_TYPES_LIST, action[8:13]))
                return action_class(trade_for)
            case ActionType.discard:
                trade_in = dict(zip(RESOURCE_TYPES_LIST, action[13:]))
                return action_class(trade_in)

from pettingzoo.test import api_test

api_test(CatanEnv(['a', 'b', 'c', 'd']))