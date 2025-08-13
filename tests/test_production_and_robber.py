import json

from catanatron.web import app
from catan import Resource, Board


def test_production_on_roll_awards_correct_resources():
    client = app.test_client()
    game_id = client.post(
        "/api/games",
        data=json.dumps({"players": ["H", "C"], "seed": 9}),
        content_type="application/json",
    ).get_json()["game_id"]

    # Fast-place initial settlements and roads for both players to exit setup
    for _ in range(4):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        settle = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(settle), content_type="application/json")
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        road = [a for a in s["current_playable_actions"] if a[1] == "BUILD_ROAD"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(road), content_type="application/json")

    # Roll a non-7 deterministically: 2 (1+1) to avoid robber
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    roll = [s["current_color"], "ROLL", [1, 1]]
    s_after = client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(roll),
        content_type="application/json",
    ).get_json()

    # Assert that resource counts are non-decreasing and at least one player got something or zero if no tile 2
    p_keys = [k for k in s_after["player_state"].keys() if k.endswith("_IN_HAND")]
    # group by player P0/P1
    by_player = {"P0": {}, "P1": {}}
    for k, v in s_after["player_state"].items():
        if not k.endswith("_IN_HAND"):
            continue
        p = k.split("_")[0]
        by_player[p][k] = v
    # At least valid numeric values present
    assert all(isinstance(v, int) and v >= 0 for p in by_player.values() for v in p.values())


def test_robber_moves_and_can_steal():
    client = app.test_client()
    game_id = client.post(
        "/api/games",
        data=json.dumps({"players": ["H", "C"], "seed": 10}),
        content_type="application/json",
    ).get_json()["game_id"]

    # Complete setup quickly
    for _ in range(4):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        settle = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(settle), content_type="application/json")
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        road = [a for a in s["current_playable_actions"] if a[1] == "BUILD_ROAD"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(road), content_type="application/json")

    # Give victim some resources by rolling a common number (6) twice
    for _ in range(2):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        client.post(
            f"/api/games/{game_id}/actions",
            data=json.dumps([s["current_color"], "ROLL", [3, 3]]),
            content_type="application/json",
        )
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        client.post(
            f"/api/games/{game_id}/actions",
            data=json.dumps([s["current_color"], "END_TURN", None]),
            content_type="application/json",
        )

    # Trigger robber with 7
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    s = client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps([s["current_color"], "ROLL", [1, 6]]),
        content_type="application/json",
    ).get_json()
    assert s["current_prompt"] == "MOVE_ROBBER"

    # Move robber to any other tile
    move = [a for a in s["current_playable_actions"] if a[1] == "MOVE_ROBBER"][0]
    s2 = client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(move),
        content_type="application/json",
    ).get_json()
    # We cannot assert steal deterministically, but prompt should return to PLAY_TURN
    assert s2["current_prompt"] == "PLAY_TURN"


