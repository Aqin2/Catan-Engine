import json

from catanatron.web import app


def create_game(client, players=("HUMAN", "CATANATRON")):
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": list(players), "seed": 2}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    return resp.get_json()["game_id"]


def test_initial_placements_and_turn_flow():
    client = app.test_client()
    game_id = create_game(client)

    # Get state; build first settlement
    s0 = client.get(f"/api/games/{game_id}/states/latest").get_json()
    settle_actions = [a for a in s0["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"]
    assert settle_actions
    client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(settle_actions[0]),
        content_type="application/json",
    )
    # Road should be available now
    s1 = client.get(f"/api/games/{game_id}/states/latest").get_json()
    road_actions = [a for a in s1["current_playable_actions"] if a[1] == "BUILD_ROAD"]
    assert road_actions
    client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(road_actions[0]),
        content_type="application/json",
    )

    # After setup complete, ROLL then END should be available on main turns
    # Fast-forward by finishing all initial placements
    # (click settlement+road pairs until initial phase is done)
    for _ in range(3):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        a = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
        client.post(
            f"/api/games/{game_id}/actions",
            data=json.dumps(a),
            content_type="application/json",
        )
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        a = [a for a in s["current_playable_actions"] if a[1] == "BUILD_ROAD"][0]
        client.post(
            f"/api/games/{game_id}/actions",
            data=json.dumps(a),
            content_type="application/json",
        )

    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    assert s["is_initial_build_phase"] is True or s["is_initial_build_phase"] is False

    if not s["is_initial_build_phase"]:
        actions = s["current_playable_actions"]
        assert [a for a in actions if a[1] == "ROLL"]
        # Roll with deterministic dice to avoid robber
        roll_action = [s["current_color"], "ROLL", [1, 1]]
        client.post(
            f"/api/games/{game_id}/actions",
            data=json.dumps(roll_action),
            content_type="application/json",
        )
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        assert [a for a in s["current_playable_actions"] if a[1] == "END_TURN"]


