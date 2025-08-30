import numpy as np
from enum import Enum

class Resource(Enum):
    brick = 'brick'
    wood =  'wood'
    wool = 'wool'
    wheat = 'wheat'
    ore = 'ore'

class Direction():
    #dirs from center of tile to corner of tile
    Q = np.array([4, -2, -2])
    R = np.array([-2, 4, -2])
    S = np.array([-2, -2, 4])
    NQ = -Q
    NR = -R
    NS = -S
    
    #dirs from center of tile to edge of tile
    QR = (Q - R) // 2
    RS = (R - S) // 2
    SQ = (S - Q) // 2
    NQR = -QR
    NRS = -RS
    NSQ = -SQ

class DevType(Enum):
    knight = 'knight'
    monopoly = 'monopoly'
    road_build = 'road_build'
    invention = 'invention'

    victory_point = 'victory_point'
