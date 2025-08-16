import numpy as np
from enum import Enum

class Resource(Enum):
    BRICK =  0
    WOOD =  1
    WOOL = 2
    WHEAT =  3
    ORE = 4
    DESERT = 5

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
    knight = 0
    monopoly = 1
    road_build = 2
    invention = 3

    victory_point = 4
