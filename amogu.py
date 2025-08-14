import numpy as np
roll_p = np.convolve(np.full((6,), 1 / 6), np.full((6,), 1 / 6))
