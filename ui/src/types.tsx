

export interface board {
    tiles: ('brick' | 'wood' | 'wood' | 'wheat' | 'ore' | 'desert')[],
    edges: (string | null)[],
    nodes: { player: string | null, value: number }[]
}

export interface game {
    players: string[],
    cur_player: string,
    expected_action?: string,
    board: board
}