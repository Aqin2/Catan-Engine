import numpy as np
from enum import Enum

class Resource(Enum):
    brick = 'brick'
    wood =  'wood'
    wool = 'wool'
    wheat = 'wheat'
    ore = 'ore'

RESOURCE_TYPES_LIST = [
    Resource.brick,
    Resource.wood,
    Resource.wool,
    Resource.wheat,
    Resource.ore
]

RESOURCE_TYPES_DICT = {
    Resource.brick: 1,
    Resource.wood: 2,
    Resource.wool: 3,
    Resource.wheat: 4,
    Resource.ore: 5
}

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

DEV_TYPES_LIST = [
    DevType.knight,
    DevType.monopoly,
    DevType.road_build,
    DevType.invention,
    DevType.victory_point
]