import json
import math

from catanatron.web import app
from catan import Board, Direction


def axial_xy(delta):
    q = float(delta[0])
    r = float(delta[2])
    x = math.sqrt(3) * q + (math.sqrt(3) / 2.0) * r
    y = 1.5 * r
    return x, y


def nearest_label(deg, targets, labels):
    idx = min(range(len(targets)), key=lambda i: min(abs(deg - targets[i]), 360 - abs(deg - targets[i])))
    return labels[idx]


def test_node_directions_center_tile_labels():
    client = app.test_client()
    game_id = client.post(
        "/api/games",
        data=json.dumps({"players": ["HUMAN", "CATANATRON"], "seed": 1}),
        content_type="application/json",
    ).get_json()["game_id"]

    state = client.get(f"/api/games/{game_id}/states/latest").get_json()

    # Expected labels from the six corner offsets using projection-based mapping
    node_targets = [0, 60, 120, 180, 240, 300]
    node_labels = ["NORTH", "NORTHEAST", "SOUTHEAST", "SOUTH", "SOUTHWEST", "NORTHWEST"]
    expected = set()
    for off in Board.NODE_OFFESTS:
        x, y = axial_xy(off)
        deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        expected.add(nearest_label(deg, node_targets, node_labels))

    center_nodes = [n for n in state["nodes"] if n["tile_coordinate"] == [0, 0, 0]]
    assert len(center_nodes) == 6
    got = {n["direction"] for n in center_nodes}
    assert got == expected


def test_edge_directions_center_tile_labels():
    client = app.test_client()
    game_id = client.post(
        "/api/games",
        data=json.dumps({"players": ["HUMAN", "CATANATRON"], "seed": 2}),
        content_type="application/json",
    ).get_json()["game_id"]

    state = client.get(f"/api/games/{game_id}/states/latest").get_json()

    edge_targets = [30, 90, 150, 210, 270, 330]
    edge_labels = ["NORTHEAST", "EAST", "SOUTHEAST", "SOUTHWEST", "WEST", "NORTHWEST"]
    expected = set()
    for off in Board.EDGE_OFFSETS:
        x, y = axial_xy(off)
        deg = (math.degrees(math.atan2(y, x)) + 360.0) % 360.0
        expected.add(nearest_label(deg, edge_targets, edge_labels))

    center_edges = [e for e in state["edges"] if e["tile_coordinate"] == [0, 0, 0]]
    assert len(center_edges) == 6
    got = {e["direction"] for e in center_edges}
    assert got == expected


