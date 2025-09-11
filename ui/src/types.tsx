export type resource = 'brick' | 'wood' | 'wood' | 'wheat' | 'ore';
export type dev_type = 'knight' | 'monopoly' | 'road_build' | 'invention' | 'victory_point';

export interface tile {
    resource: resource | 'desert',
    number: number
};

export interface board {
    tiles: tile[],
    edges: (string | null)[],
    nodes: { player: string | null, value: number }[],
    robber_tile: number
};


export interface player {
    resources: { [key in resource]: number }
    dev_cards: { [key in dev_type]: number }
};

export interface game {
    player_names: string[],
    cur_player: string,
    expected_action?: string,
    board: board,
    players: { [key: string]: player }
};