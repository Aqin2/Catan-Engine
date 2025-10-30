#worlds worst test cases

import unittest
from pettingzoo.test import api_test

from caten_env import CatanEnv

class TestCatanEnv(unittest.TestCase):
    def test_api(self):
        api_test(CatanEnv(['a_0', 'b_1', 'c_2', 'd_3']), verbose_progress=True)
    
    def test_action_mask(self):
        env = CatanEnv(['a_0', 'b_1', 'c_2', 'd_3'])
        env.reset(options={
            'record_history': True
        })
        for agent in env.agent_iter():
            obs, rew, term, trunc, info = env.last()
            if term or trunc:
                break
            
            action_mask = env.game.get_action_mask()

            legal = env.action_space(agent).sample(action_mask)

            env.step(legal)

        print(len(env.game_history))


if __name__ == '__main__':
    unittest.main()
