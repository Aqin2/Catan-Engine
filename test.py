from gymnasium import spaces
import gymnasium as gym
import numpy as np

s = spaces.Dict({
    'a': spaces.Discrete(2),
    'b': spaces.Discrete(2)
})

print(s.dtype)