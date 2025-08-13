import json

from catanatron.web import app
from catanatron.web import routes
from catan import Board


def take_first_settlement_and_road(client, game_id):
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    settle = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
    client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(settle),
        content_type="application/json",
    )
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    road = [a for a in s["current_playable_actions"] if a[1] == "BUILD_ROAD"][0]
    client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(road),
        content_type="application/json",
    )


def test_serpentine_initial_order_and_first_main_turn():
    client = app.test_client()
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": ["P0", "P1", "P2"], "seed": 42}),
        content_type="application/json",
    )
    game_id = resp.get_json()["game_id"]

    order_seen = []
    # There are 2 settlement+road pairs per player
    for _ in range(3):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        order_seen.append(s["current_color"])
        take_first_settlement_and_road(client, game_id)
    for _ in range(3):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        order_seen.append(s["current_color"])
        take_first_settlement_and_road(client, game_id)

    # Expected snake order: P0, P1, P2, P2, P1, P0 => RED, BLUE, ORANGE, ORANGE, BLUE, RED
    assert order_seen == ["RED", "BLUE", "ORANGE", "ORANGE", "BLUE", "RED"]

    # After initial placements, the last to place (P0/RED) starts the first normal turn
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    assert s["is_initial_build_phase"] is False
    assert s["current_color"] == "RED"


def test_initial_road_actions_match_adjacent_edges():
    client = app.test_client()
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": ["A", "B"], "seed": 7}),
        content_type="application/json",
    )
    game_id = resp.get_json()["game_id"]

    # Place the first settlement
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    settle = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
    client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(settle),
        content_type="application/json",
    )

    # Read debug info for last_start_node
    dbg = client.get(f"/api/debug/{game_id}/last-start-node").get_json()
    last_idx = dbg["last_start_node"]["index"]
    expected_edge_coords = {tuple(e["edge_coords"]) for e in dbg["adjacent_edges"]}

    # The offered road actions should be exactly the edges adjacent to the settlement node
    s2 = client.get(f"/api/games/{game_id}/states/latest").get_json()
    road_actions = [a for a in s2["current_playable_actions"] if a[1] == "BUILD_ROAD"]

    # Map UI road ids back to edge coordinates and compare sets (IDs must decode to the exact edge coordinates)
    game = routes.GAMES[game_id]
    got_coords = set()
    for _color, _kind, (tile_idx, dir_idx) in road_actions:
        t = game.board.tiles[int(tile_idx)]
        coord = t.coords + Board.EDGE_OFFSETS[int(dir_idx)]
        got_coords.add((int(coord[0]), int(coord[1]), int(coord[2])))

    assert got_coords == expected_edge_coords
    # Sanity: count can be 1, 2, or 3 depending on board geometry
    assert 1 <= len(road_actions) <= 3

    # Ensure the offered IDs are canonical for each edge (match lowest-index tile)
    for _color, _kind, (tile_idx, dir_idx) in road_actions:
        ecoords = (game.board.tiles[int(tile_idx)].coords + Board.EDGE_OFFSETS[int(dir_idx)])
        # Find the engine edge by coordinate
        engine_edge = game.board.edge_dict[Board.coords_hash(ecoords)]
        c_tile_idx, c_dir_idx, _dir_label, _tcoord = routes._edge_id_for_edge(game.board, engine_edge)
        assert int(tile_idx) == int(c_tile_idx)
        assert int(dir_idx) == int(c_dir_idx)


