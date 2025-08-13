from flask import jsonify, request
from catanatron.web import app, db
import uuid
from typing import Dict, List, Tuple, Any
import random

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


def str_to_resource(name: str) -> Resource:
    mapping = {
        "BRICK": Resource.BRICK,
        "WOOD": Resource.WOOD,
        "SHEEP": Resource.WOOL,
        "WHEAT": Resource.WHEAT,
        "ORE": Resource.ORE,
    }
    return mapping[name]


def serialize_tiles(board: Board) -> Tuple[List[Dict[str, Any]], List[int]]:
    """Return (tiles, robber_coordinate)."""
    tiles: List[Dict[str, Any]] = []
    robber_coord = [0, 0, 0]
    # Sort tiles by ring to ensure all 19 are emitted consistently
    # Board.generate_board added tiles in spiral order; preserve that order by using indices
    for t in board.tiles:
        coord = [int(int(t.coords[0]) // 6), int(int(t.coords[1]) // 6), int(int(t.coords[2]) // 6)]
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
                    tile_coord = [int(int(t.coords[0]) // 6), int(int(t.coords[1]) // 6), int(int(t.coords[2]) // 6)]
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
                int(int(nearest_tile.coords[0]) // 6),
                int(int(nearest_tile.coords[1]) // 6),
                int(int(nearest_tile.coords[2]) // 6),
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
                    tile_coord = [int(int(t.coords[0]) // 6), int(int(t.coords[1]) // 6), int(int(t.coords[2]) // 6)]
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
                int(int(nearest_tile.coords[0]) // 6),
                int(int(nearest_tile.coords[1]) // 6),
                int(int(nearest_tile.coords[2]) // 6),
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
        # main turn
        color = map_players_to_colors(game.players)[game.cur_player]
        if game.move_robber_pending:
            # Allow selecting robber destination
            for t in game.board.tiles:
                coord = [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])]
                if coord == [int(game.robber_coords[0]), int(game.robber_coords[1]), int(game.robber_coords[2])]:
                    continue
                actions.append([color, "MOVE_ROBBER", [coord, None, None]])
            return actions
        if not game.has_rolled:
            actions.append([color, "ROLL", None])
        else:
            # Build options based on resources and stocks
            # Roads
            for e in game.board.edges:
                if not _edge_valid_for_player(game.board, e, game.cur_player):
                    continue
                # Check pieces and resources or free roads
                if game.player_pieces[game.cur_player]["roads"] <= 0:
                    break
                have_free = game.free_roads_remaining[game.cur_player] > 0
                have_res = (
                    game.player_resources[game.cur_player][Resource.WOOD] >= 1
                    and game.player_resources[game.cur_player][Resource.BRICK] >= 1
                )
                if not (have_free or have_res):
                    pass
                else:
                    for t in game.board.tiles:
                        delta = e.coords - t.coords
                        for dir_idx, off in enumerate(Board.EDGE_OFFSETS):
                            if (delta == off).all():
                                actions.append([
                                    color,
                                    "BUILD_ROAD",
                                    [int(t.index), int(dir_idx)],
                                ])
                                break
                        else:
                            continue
                        break

            # Settlements
            if game.player_pieces[game.cur_player]["settlements"] > 0:
                for n in game.board.nodes:
                    if not n.available:
                        continue
                    # Must be connected to own road
                    connected = False
                    for adj_edge_idx in Board.node_edge_list[n.index]:
                        if game.board.edges[adj_edge_idx].player == game.cur_player:
                            connected = True
                            break
                    if not connected:
                        continue
                    have_res = (
                        game.player_resources[game.cur_player][Resource.WOOD] >= 1
                        and game.player_resources[game.cur_player][Resource.BRICK] >= 1
                        and game.player_resources[game.cur_player][Resource.WHEAT] >= 1
                        and game.player_resources[game.cur_player][Resource.WOOL] >= 1
                    )
                    if have_res:
                        actions.append([color, "BUILD_SETTLEMENT", int(n.index)])

            # Cities
            if game.player_pieces[game.cur_player]["cities"] > 0:
                for n in game.board.nodes:
                    if n.player == game.cur_player and getattr(n, "value", 0) == 1:
                        have_res = (
                            game.player_resources[game.cur_player][Resource.WHEAT] >= 2
                            and game.player_resources[game.cur_player][Resource.ORE] >= 3
                        )
                        if have_res:
                            actions.append([color, "BUILD_CITY", int(n.index)])

            # Buy development card
            if (
                game.player_resources[game.cur_player][Resource.WHEAT] >= 1
                and game.player_resources[game.cur_player][Resource.WOOL] >= 1
                and game.player_resources[game.cur_player][Resource.ORE] >= 1
            ):
                actions.append([color, "BUY_DEVELOPMENT_CARD", None])

            # Play dev cards if owned (presence enables UI menus; selection will be sent later)
            if game.player_devs_in_hand[game.cur_player]["KNIGHT"] > 0:
                actions.append([color, "PLAY_KNIGHT_CARD", None])
            if game.player_devs_in_hand[game.cur_player]["ROAD_BUILDING"] > 0:
                actions.append([color, "PLAY_ROAD_BUILDING", None])
            if game.player_devs_in_hand[game.cur_player]["YEAR_OF_PLENTY"] > 0:
                actions.append([color, "PLAY_YEAR_OF_PLENTY", None])
            if game.player_devs_in_hand[game.cur_player]["MONOPOLY"] > 0:
                actions.append([color, "PLAY_MONOPOLY", None])

            # Maritime trades based on current bank rates
            res_list = [Resource.WOOD, Resource.BRICK, Resource.WOOL, Resource.WHEAT, Resource.ORE]
            pr = game.player_resources[game.cur_player]
            for give in res_list:
                rate = game.bank_trade_rates[game.cur_player][give]
                if pr[give] >= rate:
                    for receive in res_list:
                        # Build 5-tuple arg for UI humanizer: up to 4 gives + 1 receive
                        gives = [resource_to_str(give)] * min(rate, 4)
                        while len(gives) < 4:
                            gives.append(None)
                        actions.append([color, "MARITIME_TRADE", gives + [resource_to_str(receive)]])

            # End turn always available after roll
            actions.append([color, "END_TURN", None])
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
    tiles, _robber_from_tiles = serialize_tiles(game.board)
    player_to_color = map_players_to_colors(game.players)
    colors = [player_to_color[p] for p in game.players]
    current_color = player_to_color[game.cur_player]
    # Treat all players as human for now to avoid UI auto-playing bot turns
    bot_colors = []

    nodes = serialize_nodes(game.board, player_to_color)
    edges = serialize_edges(game.board, player_to_color)

    current_playable_actions = compute_current_playable_actions(game)

    # Build player_state with resource counts and flags
    player_state: Dict[str, Any] = {}
    for idx, player in enumerate(game.players):
        key = f"P{idx}"
        # resources from engine
        player_state[f"{key}_WOOD_IN_HAND"] = game.player_resources[player][Resource.WOOD]
        player_state[f"{key}_BRICK_IN_HAND"] = game.player_resources[player][Resource.BRICK]
        player_state[f"{key}_SHEEP_IN_HAND"] = game.player_resources[player][Resource.WOOL]
        player_state[f"{key}_WHEAT_IN_HAND"] = game.player_resources[player][Resource.WHEAT]
        player_state[f"{key}_ORE_IN_HAND"] = game.player_resources[player][Resource.ORE]
        # dev and flags defaults
        player_state[f"{key}_VICTORY_POINT_IN_HAND"] = game.player_devs_in_hand[player]["VICTORY_POINT"]
        player_state[f"{key}_KNIGHT_IN_HAND"] = game.player_devs_in_hand[player]["KNIGHT"]
        player_state[f"{key}_MONOPOLY_IN_HAND"] = game.player_devs_in_hand[player]["MONOPOLY"]
        player_state[f"{key}_YEAR_OF_PLENTY_IN_HAND"] = game.player_devs_in_hand[player]["YEAR_OF_PLENTY"]
        player_state[f"{key}_ROAD_BUILDING_IN_HAND"] = game.player_devs_in_hand[player]["ROAD_BUILDING"]
        player_state[f"{key}_HAS_ROLLED"] = game.has_rolled if player == game.cur_player else False

    robber_coordinate = [int(game.robber_coords[0]), int(game.robber_coords[1]), int(game.robber_coords[2])]

    # Compute victory points and winning color
    def compute_vp_for(player: str) -> int:
        vp = 0
        # settlements and cities
        for n in game.board.nodes:
            if n.player == player:
                if getattr(n, "value", 0) == 1:
                    vp += 1
                elif getattr(n, "value", 0) == 2:
                    vp += 2
        # dev VP
        vp += game.player_devs_in_hand[player]["VICTORY_POINT"]
        # awards
        if getattr(game, "largest_army_owner", None) == player:
            vp += 2
        if getattr(game, "longest_road_owner", None) == player:
            vp += 2
        return vp

    player_to_color = map_players_to_colors(game.players)
    winning_color = None
    for p in game.players:
        if compute_vp_for(p) >= 10:
            winning_color = player_to_color[p]
            break

    game_state: Dict[str, Any] = {
        "tiles": tiles,
        "adjacent_tiles": {},  # optional, not used by UI now
        "bot_colors": bot_colors,
        "colors": colors,
        "current_color": current_color,
        "winning_color": winning_color,
        "current_prompt": (
            "START_PLACEMENT"
            if len(game.action_queue) > 0
            else ("MOVE_ROBBER" if game.move_robber_pending else "PLAY_TURN")
        ),
        "player_state": player_state,
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
        # initial placements are free
        if len(game.action_queue) > 0:
            ok = game.step(StructureAction(coords=node.coords, value=1))
        else:
            # check resources and pieces
            pr = game.player_resources[game.cur_player]
            if (
                game.player_pieces[game.cur_player]["settlements"] > 0
                and pr[Resource.WOOD] >= 1
                and pr[Resource.BRICK] >= 1
                and pr[Resource.WHEAT] >= 1
                and pr[Resource.WOOL] >= 1
            ):
                ok = game.board.place_structure(node.coords, game.cur_player, 1, starting=False)
                if ok:
                    pr[Resource.WOOD] -= 1
                    pr[Resource.BRICK] -= 1
                    pr[Resource.WHEAT] -= 1
                    pr[Resource.WOOL] -= 1
                    game.player_pieces[game.cur_player]["settlements"] -= 1
            else:
                ok = False
    elif kind == "BUILD_ROAD" and isinstance(arg, list) and len(arg) == 2:
        tile_idx, dir_idx = arg
        try:
            t = game.board.tiles[int(tile_idx)]
            coords = t.coords + Board.EDGE_OFFSETS[int(dir_idx)]
        except Exception:
            return jsonify({"error": "invalid edge id"}), 400
        # Validate adjacency strictly based on the last placed settlement during setup
        if len(game.action_queue) > 0:
            # Road must be one of the two edges adjacent to the just-placed settlement
            last_idx = getattr(game, "last_start_node_idx", None)
            valid_adj = False
            if last_idx is not None:
                for eidx in Board.node_edge_list[last_idx]:
                    if (game.board.edges[eidx].coords == coords).all():
                        valid_adj = True
                        break
            if not valid_adj:
                ok = False
            else:
                ok = game.step(RoadAction(coords=coords))
        else:
            have_free = game.free_roads_remaining[game.cur_player] > 0
            pr = game.player_resources[game.cur_player]
            have_res = pr[Resource.WOOD] >= 1 and pr[Resource.BRICK] >= 1
            if game.player_pieces[game.cur_player]["roads"] > 0 and (have_free or have_res):
                ok = game.board.place_road(coords, game.cur_player)
                if ok:
                    if have_free:
                        game.free_roads_remaining[game.cur_player] -= 1
                    else:
                        pr[Resource.WOOD] -= 1
                        pr[Resource.BRICK] -= 1
                    game.player_pieces[game.cur_player]["roads"] -= 1
            else:
                ok = False
    elif kind == "BUILD_CITY" and isinstance(arg, int):
        try:
            node = game.board.nodes[arg]
        except Exception:
            return jsonify({"error": "invalid node id"}), 400
        if (
            node.player == game.cur_player
            and getattr(node, "value", 0) == 1
            and game.player_pieces[game.cur_player]["cities"] > 0
            and game.player_resources[game.cur_player][Resource.WHEAT] >= 2
            and game.player_resources[game.cur_player][Resource.ORE] >= 3
        ):
            node.value = 2
            game.player_resources[game.cur_player][Resource.WHEAT] -= 2
            game.player_resources[game.cur_player][Resource.ORE] -= 3
            game.player_pieces[game.cur_player]["cities"] -= 1
            ok = True
        else:
            ok = False
    elif kind == "ROLL":
        # Mark rolled; production handling comes later
        game.has_rolled = True
        # Allow tests to pass deterministic dice
        if isinstance(arg, list) and len(arg) == 2:
            d1, d2 = int(arg[0]), int(arg[1])
        else:
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
        total = d1 + d2
        if total == 7:
            game.move_robber_pending = True
        else:
            # production: for each tile with matching number, award resources by adjacent settlements/cities
            for t in game.board.tiles:
                if int(t.number) != total:
                    continue
                if t.resource == Resource.DESERT:
                    continue
                for n in game.board.nodes:
                    # adjacent if node.coords == t.coords + any NODE_OFFESTS
                    delta = n.coords - t.coords
                    is_adj = False
                    for off in Board.NODE_OFFESTS:
                        if (delta == off).all():
                            is_adj = True
                            break
                    if not is_adj:
                        continue
                    if n.player is None or getattr(n, "value", 0) == 0:
                        continue
                    qty = 1 if n.value == 1 else 2
                    game.player_resources[n.player][t.resource] += qty
        ok = True
        game.actions_log.append([color, "ROLL", [d1, d2]])
    elif kind == "MOVE_ROBBER" and isinstance(arg, list) and len(arg) >= 1:
        # arg: [tileCoord, targetColor?, resource?]
        tile_coord = arg[0]
        game.robber_coords = Board.tiles[0].coords if False else game.robber_coords  # no-op for type
        game.robber_coords = (lambda a: __import__('numpy').array(a)) (tile_coord)
        # Optional steal: find opponents on adjacent nodes, steal one resource randomly
        opponents = set()
        for n in game.board.nodes:
            delta = n.coords - game.robber_coords
            for off in Board.NODE_OFFESTS:
                if (delta == off).all():
                    if n.player and n.player != game.cur_player:
                        opponents.add(n.player)
                    break
        stolen_res_name = None
        if opponents:
            victim = next(iter(opponents))
            # pick a resource the victim has
            avail = [r for r, cnt in game.player_resources[victim].items() if cnt > 0]
            if avail:
                res = random.choice(avail)
                game.player_resources[victim][res] -= 1
                game.player_resources[game.cur_player][res] += 1
                stolen_res_name = resource_to_str(res)
        game.move_robber_pending = False
        ok = True
    elif kind == "END_TURN":
        if len(game.action_queue) == 0 and game.has_rolled:
            # recompute longest road owner before advancing
            best_len = 0
            owner = None
            for p in game.players:
                lr = game.board.longest_road(p)
                if lr > best_len and lr >= 5:
                    best_len = lr
                    owner = p
            game.longest_road_owner = owner
            game.advance_player()
            ok = True
            game.actions_log.append([color, "END_TURN", None])
        else:
            ok = False
    elif kind == "BUY_DEVELOPMENT_CARD":
        pr = game.player_resources[game.cur_player]
        if pr[Resource.WHEAT] >= 1 and pr[Resource.WOOL] >= 1 and pr[Resource.ORE] >= 1:
            pr[Resource.WHEAT] -= 1
            pr[Resource.WOOL] -= 1
            pr[Resource.ORE] -= 1
            # simple deck: rotate through types
            order = ["KNIGHT", "ROAD_BUILDING", "YEAR_OF_PLENTY", "MONOPOLY", "VICTORY_POINT"]
            idx = sum(sum(v.values()) for v in game.player_devs_in_hand.values()) % len(order)
            picked = order[idx]
            game.player_devs_in_hand[game.cur_player][picked] += 1
            ok = True
        else:
            ok = False
    elif kind == "PLAY_KNIGHT_CARD":
        if game.player_devs_in_hand[game.cur_player]["KNIGHT"] > 0:
            game.player_devs_in_hand[game.cur_player]["KNIGHT"] -= 1
            game.knights_played[game.cur_player] += 1
            # largest army reevaluation
            best = max(game.knights_played.values())
            owners = [p for p, v in game.knights_played.items() if v == best]
            if best >= 3 and len(owners) == 1:
                game.largest_army_owner = owners[0]
            game.move_robber_pending = True
            ok = True
        else:
            ok = False
    elif kind == "PLAY_ROAD_BUILDING":
        if game.player_devs_in_hand[game.cur_player]["ROAD_BUILDING"] > 0:
            game.player_devs_in_hand[game.cur_player]["ROAD_BUILDING"] -= 1
            game.free_roads_remaining[game.cur_player] = 2
            ok = True
        else:
            ok = False
    elif kind == "PLAY_YEAR_OF_PLENTY" and isinstance(arg, list):
        # Accept one or two resources
        res_names = [x for x in arg if x is not None][:2]
        if game.player_devs_in_hand[game.cur_player]["YEAR_OF_PLENTY"] > 0 and 1 <= len(res_names) <= 2:
            for name in res_names:
                game.player_resources[game.cur_player][str_to_resource(name)] += 1
            game.player_devs_in_hand[game.cur_player]["YEAR_OF_PLENTY"] -= 1
            ok = True
        else:
            ok = False
    elif kind == "PLAY_MONOPOLY" and isinstance(arg, str):
        if game.player_devs_in_hand[game.cur_player]["MONOPOLY"] > 0:
            res = str_to_resource(arg)
            total_taken = 0
            for p in game.players:
                if p == game.cur_player:
                    continue
                cnt = game.player_resources[p][res]
                if cnt > 0:
                    total_taken += cnt
                    game.player_resources[p][res] = 0
            game.player_resources[game.cur_player][res] += total_taken
            game.player_devs_in_hand[game.cur_player]["MONOPOLY"] -= 1
            ok = True
        else:
            ok = False
    elif kind == "MARITIME_TRADE" and isinstance(arg, list) and len(arg) == 5:
        # arg: [g,g,g,g, receive], where g may be None; 2-4 of them depending on port
        receive = str_to_resource(arg[4])
        gives = [x for x in arg[:4] if x is not None]
        if not gives:
            ok = False
        else:
            give_res = str_to_resource(gives[0])
            rate = game.bank_trade_rates[game.cur_player][give_res]
            if len(gives) >= rate and all(x == gives[0] for x in gives):
                if game.player_resources[game.cur_player][give_res] >= rate:
                    game.player_resources[game.cur_player][give_res] -= rate
                    game.player_resources[game.cur_player][receive] += 1
                    ok = True
                else:
                    ok = False
            else:
                ok = False
    else:
        # For now, ignore other actions
        ok = False

    if not ok:
        # Return current state without changes; UI can treat as no-op
        return jsonify(serialize_game(game))

    return jsonify(serialize_game(game))


# --- Debug endpoints ---
@app.route('/api/debug/<game_id>/last-start-node')
def debug_last_start_node(game_id):
    game = GAMES.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    idx = getattr(game, "last_start_node_idx", None)
    if idx is None:
        return jsonify({"last_start_node": None})
    node = game.board.nodes[idx]
    edges = []
    for eidx in Board.node_edge_list[idx]:
        e = game.board.edges[eidx]
        # find tile+dir id like the UI uses
        mapping = []
        for t in game.board.tiles:
            delta = e.coords - t.coords
            for dir_idx, off in enumerate(Board.EDGE_OFFSETS):
                if (delta == off).all():
                    mapping.append({
                        "tile_index": int(t.index),
                        "dir_index": int(dir_idx),
                        "tile_coord": [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])],
                    })
        edges.append({
            "edge_index": int(e.index),
            "edge_coords": [int(e.coords[0]), int(e.coords[1]), int(e.coords[2])],
            "ui_ids": mapping,
        })
    return jsonify({
        "last_start_node": {
            "index": int(node.index),
            "coords": [int(node.coords[0]), int(node.coords[1]), int(node.coords[2])],
        },
        "adjacent_edges": edges,
    })


@app.route('/api/debug/<game_id>/tiles')
def debug_tiles(game_id):
    game = GAMES.get(game_id)
    if not game:
        return jsonify({"error": "game not found"}), 404
    tiles = [
        {
            "index": int(t.index),
            "coord": [int(t.coords[0]), int(t.coords[1]), int(t.coords[2])],
            "resource": resource_to_str(t.resource),
            "number": int(t.number),
        }
        for t in game.board.tiles
    ]
    return jsonify({"count": len(tiles), "tiles": tiles})
