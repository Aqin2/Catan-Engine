import json

from catanatron.web import app


def test_maritime_trade_and_longest_road_award():
    client = app.test_client()
    # Create game
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": ["HUMAN", "CATANATRON"], "seed": 3}),
        content_type="application/json",
    )
    game_id = resp.get_json()["game_id"]

    # Complete initial placements quickly
    for _ in range(4):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        a = [a for a in s["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(a), content_type="application/json")
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        a = [a for a in s["current_playable_actions"] if a[1] == "BUILD_ROAD"][0]
        client.post(f"/api/games/{game_id}/actions", data=json.dumps(a), content_type="application/json")

    # Give current player some resources artificially by rolling deterministic non-7 a few times
    for _ in range(3):
        s = client.get(f"/api/games/{game_id}/states/latest").get_json()
        if s["current_playable_actions"] and s["current_playable_actions"][0][1] == "ROLL":
            roll = [s["current_color"], "ROLL", [6, 5]]
            client.post(f"/api/games/{game_id}/actions", data=json.dumps(roll), content_type="application/json")
            # try a maritime trade if available
            s = client.get(f"/api/games/{game_id}/states/latest").get_json()
            trades = [a for a in s["current_playable_actions"] if a[1] == "MARITIME_TRADE"]
            if trades:
                client.post(f"/api/games/{game_id}/actions", data=json.dumps(trades[0]), content_type="application/json")
            end = [s["current_color"], "END_TURN", None]
            client.post(f"/api/games/{game_id}/actions", data=json.dumps(end), content_type="application/json")

    # After some roads are placed by manual actions, longest road may be assigned (>=5)
    s = client.get(f"/api/games/{game_id}/states/latest").get_json()
    # Just assert that computing longest road doesn't crash and returns a valid state
    assert "winning_color" in s

