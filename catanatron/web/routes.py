from flask import jsonify, request
from catanatron.web import app, db
import uuid
from typing import Dict, List, Tuple, Any

# Import the game logic
from catan import Resource, Board, Game, Node, Edge


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
    NODE_DIR_LABELS = [
        "NORTH",
        "NORTHEAST",
        "SOUTHEAST",
        "SOUTH",
        "SOUTHWEST",
        "NORTHWEST",
    ]

    nodes: List[Dict[str, Any]] = []
    for n in board.nodes:
        found = False
        for t in board.tiles:
            delta = n.coords - t.coords
            for dir_idx, off in enumerate(Board.NODE_OFFESTS):
                if (delta == off).all():
                    tile_coord = [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])]
                    direction = NODE_DIR_LABELS[dir_idx]
                    building = (
                        "CITY"
                        if getattr(n, "value", 0) == 2
                        else ("SETTLEMENT" if getattr(n, "value", 0) == 1 else None)
                    )
                    owner = (
                        color_map.get(getattr(n, "player", None), None)
                        if getattr(n, "player", None)
                        else None
                    )
                    nodes.append(
                        {
                            "id": int(n.index),
                            "tile_coordinate": tile_coord,
                            "direction": direction,
                            "building": building,
                            "color": owner,
                        }
                    )
                    found = True
                    break
            if found:
                break
        if not found:
            # Fallback to nearest tile, NORTH direction
            nearest_tile = min(
                board.tiles,
                key=lambda t: int(
                    abs(n.coords[0] - t.coords[0])
                    + abs(n.coords[1] - t.coords[1])
                    + abs(n.coords[2] - t.coords[2])
                ),
            )
            tile_coord = [
                int(nearest_tile.coords[0]),
                int(nearest_tile.coords[1]),
                int(nearest_tile.coords[2]),
            ]
            building = (
                "CITY"
                if getattr(n, "value", 0) == 2
                else ("SETTLEMENT" if getattr(n, "value", 0) == 1 else None)
            )
            owner = (
                color_map.get(getattr(n, "player", None), None)
                if getattr(n, "player", None)
                else None
            )
            nodes.append(
                {
                    "id": int(n.index),
                    "tile_coordinate": tile_coord,
                    "direction": "NORTH",
                    "building": building,
                    "color": owner,
                }
            )
    return nodes


def serialize_edges(board: Board, color_map: Dict[str, str]) -> List[Dict[str, Any]]:
    EDGE_DIR_LABELS = [
        "NORTHEAST",
        "EAST",
        "SOUTHEAST",
        "SOUTHWEST",
        "WEST",
        "NORTHWEST",
    ]

    edges: List[Dict[str, Any]] = []
    for e in board.edges:
        found = False
        for t in board.tiles:
            delta = e.coords - t.coords
            for dir_idx, off in enumerate(Board.EDGE_OFFSETS):
                if (delta == off).all():
                    tile_coord = [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])]
                    direction = EDGE_DIR_LABELS[dir_idx]
                    owner = (
                        color_map.get(getattr(e, "player", None), None)
                        if getattr(e, "player", None)
                        else None
                    )
                    edges.append(
                        {
                            "id": [int(t.index), int(dir_idx)],
                            "color": owner,
                            "direction": direction,
                            "tile_coordinate": tile_coord,
                        }
                    )
                    found = True
                    break
            if found:
                break
        if not found:
            # Fallback to nearest tile and canonical direction
            nearest_tile = min(
                board.tiles,
                key=lambda t: int(
                    abs(e.coords[0] - t.coords[0])
                    + abs(e.coords[1] - t.coords[1])
                    + abs(e.coords[2] - t.coords[2])
                ),
            )
            tile_coord = [
                int(nearest_tile.coords[0]),
                int(nearest_tile.coords[1]),
                int(nearest_tile.coords[2]),
            ]
            owner = (
                color_map.get(getattr(e, "player", None), None)
                if getattr(e, "player", None)
                else None
            )
            edges.append(
                {
                    "id": [int(nearest_tile.index), 0],
                    "color": owner,
                    "direction": EDGE_DIR_LABELS[0],
                    "tile_coordinate": tile_coord,
                }
            )
    return edges


def _node_blocked_by_opponent(board: Board, node: Node, player: str) -> bool:
    return node.player is not None and node.player != player


def _edge_valid_for_player(board: Board, edge: Edge, player: str) -> bool:
    if edge.player:
        return False
    node_indices = Board.edge_node_list[edge.index]
    nodes = [board.nodes[i] for i in node_indices]
    for n in nodes:
        if _node_blocked_by_opponent(board, n, player):
            continue
        # Connected to own settlement/city
        if n.player == player:
            return True
        # Or connected to own road via this node
        for adj_edge_idx in Board.node_edge_list[n.index]:
            if adj_edge_idx == edge.index:
                continue
            if board.edges[adj_edge_idx].player == player:
                return True
    return False


def compute_current_playable_actions(game: Game) -> List[Any]:
    actions: List[Any] = []
    if len(game.action_queue) == 0:
        return actions

    player_to_color = map_players_to_colors(game.players)
    color = player_to_color[game.cur_player]
    head = game.action_queue[0]
    if head.name == "structure":
        for n in game.board.nodes:
            if n.available:
                actions.append([color, "BUILD_SETTLEMENT", int(n.index)])
    elif head.name == "road":
        for e in game.board.edges:
            if not _edge_valid_for_player(game.board, e, game.cur_player):
                continue
            # Find the tile+direction id used by UI
            for t in game.board.tiles:
                delta = e.coords - t.coords
                for dir_idx, off in enumerate(Board.EDGE_OFFSETS):
                    if (delta == off).all():
                        actions.append([color, "BUILD_ROAD", [int(t.index), int(dir_idx)]])
                        break
                else:
                    continue
                break
    return actions


def serialize_game(game: Game) -> Dict[str, Any]:
    tiles, robber_coordinate = serialize_tiles(game.board)
    player_to_color = map_players_to_colors(game.players)
    colors = [player_to_color[p] for p in game.players]
    current_color = player_to_color[game.cur_player]
    # Treat all players as human for now to avoid UI auto-playing bot turns
    bot_colors = []

    nodes = serialize_nodes(game.board, player_to_color)
    edges = serialize_edges(game.board, player_to_color)

    current_playable_actions = compute_current_playable_actions(game)

    game_state: Dict[str, Any] = {
        "tiles": tiles,
        "adjacent_tiles": {},  # optional, not used by UI now
        "bot_colors": bot_colors,
        "colors": colors,
        "current_color": current_color,
        "winning_color": None,
        "current_prompt": (
            "PLAY_TURN" if len(game.action_queue) == 0 and not game.has_rolled else (
                "MOVE_ROBBER" if False else "PLAY_TURN"
            )
        ) if len(game.action_queue) == 0 else "START_PLACEMENT",
        "player_state": {},
        "actions": getattr(game, "actions_log", []),
        "robber_coordinate": robber_coordinate,
        "nodes": nodes,
        "edges": edges,
        "current_playable_actions": current_playable_actions,
        "is_initial_build_phase": len(game.action_queue) > 0,
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
    game = GAMES.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    payload = request.get_json(silent=True)
    if not payload:
        # No-op (bots not implemented yet)
        return jsonify(serialize_game(game))

    try:
        color, kind, arg = payload
    except Exception:
        return jsonify({"error": "invalid action format"}), 400

    from catan import StructureAction, RoadAction

    ok = False
    if kind == "BUILD_SETTLEMENT" and isinstance(arg, int):
        # Find node by id
        try:
            node = game.board.nodes[arg]
        except Exception:
            return jsonify({"error": "invalid node id"}), 400
        ok = game.step(StructureAction(coords=node.coords, value=1))
    elif kind == "BUILD_ROAD" and isinstance(arg, list) and len(arg) == 2:
        tile_idx, dir_idx = arg
        try:
            t = game.board.tiles[int(tile_idx)]
            coords = t.coords + Board.EDGE_OFFSETS[int(dir_idx)]
        except Exception:
            return jsonify({"error": "invalid edge id"}), 400
        ok = game.step(RoadAction(coords=coords))
    elif kind == "ROLL":
        # Mark rolled; production handling comes later
        game.has_rolled = True
        ok = True
        game.actions_log.append([color, "ROLL", None])
    elif kind == "END_TURN":
        if len(game.action_queue) == 0 and game.has_rolled:
            game.advance_player()
            ok = True
            game.actions_log.append([color, "END_TURN", None])
        else:
            ok = False
    else:
        # For now, ignore other actions
        ok = False

    if not ok:
        # Return current state without changes; UI can treat as no-op
        return jsonify(serialize_game(game))

    return jsonify(serialize_game(game))
