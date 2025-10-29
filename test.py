from gymnasium import spaces
import numpy as np
x = spaces.MultiDiscrete([10, 10])

x.sample((np.array([1, 1, 1, 1, 1, 0, 0, 0, 0,0], dtype=np.int8), None))