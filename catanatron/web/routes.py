from flask import jsonify, request
from catanatron.web import app, db
import uuid
from typing import Dict, List, Tuple, Any

# Import the game logic
from catan import Resource, Board, Game


# In-memory game registry (phase 2)
GAMES: Dict[str, Game] = {}


# ----- Phase 1: Define and serialize GameState to match UI ----- #

COLOR_ORDER = ["RED", "BLUE", "ORANGE", "WHITE"]


def map_players_to_colors(players: List[str]) -> Dict[str, str]:
    return {player: COLOR_ORDER[i] for i, player in enumerate(players)}


def resource_to_str(res: Resource) -> str:
    if res == Resource.BRICK:
        return "BRICK"
    if res == Resource.WOOD:
        return "WOOD"
    if res == Resource.WOOL:
        return "SHEEP"  # UI type uses SHEEP instead of WOOL
    if res == Resource.WHEAT:
        return "WHEAT"
    if res == Resource.ORE:
        return "ORE"
    if res == Resource.DESERT:
        return "DESERT"
    raise ValueError(f"Unknown resource: {res}")


def serialize_tiles(board: Board) -> Tuple[List[Dict[str, Any]], List[int]]:
    """Return (tiles, robber_coordinate)."""
    tiles: List[Dict[str, Any]] = []
    robber_coord = [0, 0, 0]
    for t in board.tiles:
        coord = [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])]
        if t.resource == Resource.DESERT:
            tiles.append({
                "coordinate": coord,
                "tile": {"id": t.index, "type": "DESERT"},
            })
            robber_coord = coord
        else:
            tiles.append({
                "coordinate": coord,
                "tile": {
                    "id": t.index,
                    "type": "RESOURCE_TILE",
                    "resource": resource_to_str(t.resource),
                    "number": int(t.number),
                },
            })
    return tiles, robber_coord


def serialize_nodes(board: Board, color_map: Dict[str, str]) -> List[Dict[str, Any]]:
    """Minimal node serialization without exact direction mapping yet.
    We associate each node with an arbitrary adjacent tile and a default
    direction to render reasonably. This completes Phase 1 contract.
    """
    nodes: List[Dict[str, Any]] = []
    # Pick the closest tile center to define tile_coordinate
    for n in board.nodes:
        # Choose any adjacent tile by nearest Manhattan distance in this coordinate system
        nearest_tile = min(board.tiles, key=lambda t: int(abs(n.coords[0]-t.coords[0]) + abs(n.coords[1]-t.coords[1]) + abs(n.coords[2]-t.coords[2])))
        tile_coord = [int(nearest_tile.coords[0]), int(nearest_tile.coords[1]), int(nearest_tile.coords[2])]
        direction = "NORTH"  # placeholder; will refine in Phase 3
        building = "CITY" if getattr(n, "value", 0) == 2 else ("SETTLEMENT" if getattr(n, "value", 0) == 1 else None)
        owner = color_map.get(getattr(n, "player", None), None) if getattr(n, "player", None) else None
        nodes.append({
            "id": int(n.index),
            "tile_coordinate": tile_coord,
            "direction": direction,
            "building": building,
            "color": owner,
        })
    return nodes


def serialize_edges(board: Board, color_map: Dict[str, str]) -> List[Dict[str, Any]]:
    edges: List[Dict[str, Any]] = []
    for e in board.edges:
        # Bind to nearest tile center (similar approach as nodes)
        nearest_tile = min(board.tiles, key=lambda t: int(abs(e.coords[0]-t.coords[0]) + abs(e.coords[1]-t.coords[1]) + abs(e.coords[2]-t.coords[2])))
        tile_coord = [int(nearest_tile.coords[0]), int(nearest_tile.coords[1]), int(nearest_tile.coords[2])]
        # Direction placeholder mapping index->UI label (to refine in Phase 3)
        # This keeps visual consistency even if rotated.
        dir_cycle = ["NORTHEAST", "EAST", "SOUTHEAST", "SOUTHWEST", "WEST", "NORTHWEST"]
        direction = dir_cycle[e.index % 6]
        owner = color_map.get(getattr(e, "player", None), None) if getattr(e, "player", None) else None
        edges.append({
            "id": [int(nearest_tile.index), int(e.index % 6)],
            "color": owner,
            "direction": direction,
            "tile_coordinate": tile_coord,
        })
    return edges


def serialize_game(game: Game) -> Dict[str, Any]:
    tiles, robber_coordinate = serialize_tiles(game.board)
    player_to_color = map_players_to_colors(game.players)
    colors = [player_to_color[p] for p in game.players]
    current_color = player_to_color[game.cur_player]
    # Everyone except HUMAN is a bot (simple rule for now)
    bot_colors = [player_to_color[p] for p in game.players if p != "HUMAN"]

    nodes = serialize_nodes(game.board, player_to_color)
    edges = serialize_edges(game.board, player_to_color)

    game_state: Dict[str, Any] = {
        "tiles": tiles,
        "adjacent_tiles": {},  # optional, not used by UI now
        "bot_colors": bot_colors,
        "colors": colors,
        "current_color": current_color,
        "winning_color": None,
        "current_prompt": "PLAY_TURN",  # placeholder prompt
        "player_state": {},  # can be populated later
        "actions": [],
        "robber_coordinate": robber_coordinate,
        "nodes": nodes,
        "edges": edges,
        "current_playable_actions": [],
        "is_initial_build_phase": True,
    }
    return game_state


@app.route('/api/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json() or {}
        players = data.get('players', [])
        seed = data.get('seed')
        if not players:
            return jsonify({"error": "players array required"}), 400
        if len(players) > 4:
            return jsonify({"error": "max 4 players supported"}), 400

        game = Game(players=players, seed=seed)
        game_id = str(uuid.uuid4())
        GAMES[game_id] = game
        return jsonify({
            "game_id": game_id,
            "message": "Game created successfully",
            "players": players,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/games/<game_id>/states/<state_index>')
def get_state(game_id, state_index):
    game = GAMES.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    state = serialize_game(game)
    return jsonify(state)


@app.route('/api/games/<game_id>/actions', methods=['POST'])
def post_action(game_id):
    # Phase 2 placeholder: simply return current state until full action handling is implemented
    game = GAMES.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    state = serialize_game(game)
    return jsonify(state)
