import json

from catanatron.web import app


def test_create_game_and_initial_actions():
    client = app.test_client()

    # Create game
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": ["HUMAN", "CATANATRON"], "seed": 1}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    game_id = resp.get_json()["game_id"]

    # Get state
    resp = client.get(f"/api/games/{game_id}/states/latest")
    assert resp.status_code == 200
    state = resp.get_json()
    assert state["is_initial_build_phase"] is True
    # Settlement actions should be present
    settlement_actions = [a for a in state["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"]
    assert len(settlement_actions) > 0

    # Take first settlement action
    action = settlement_actions[0]
    resp = client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(action),
        content_type="application/json",
    )
    assert resp.status_code == 200
    state = resp.get_json()

    # Should now be road actions for same player
    road_actions = [a for a in state["current_playable_actions"] if a[1] == "BUILD_ROAD"]
    assert len(road_actions) > 0

    # Take a road action
    action = road_actions[0]
    resp = client.post(
        f"/api/games/{game_id}/actions",
        data=json.dumps(action),
        content_type="application/json",
    )
    assert resp.status_code == 200
    state = resp.get_json()

    # After placing road, still in initial phase (next player's turn)
    assert state["is_initial_build_phase"] is True

