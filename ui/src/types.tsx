export interface tile {
    resource: 'brick' | 'wood' | 'wood' | 'wheat' | 'ore' | 'desert',
    number: number
}

export interface board {
    tiles: tile[],
    edges: (string | null)[],
    nodes: { player: string | null, value: number }[],
    robber_tile: number
}

export interface game {
    players: string[],
    cur_player: string,
    expected_action?: string,
    board: board
}