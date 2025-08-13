import json

from catanatron.web import app, routes


def test_all_available_nodes_are_placeable_initial_phase():
    client = app.test_client()
    resp = client.post(
        "/api/games",
        data=json.dumps({"players": ["HUMAN", "CATANATRON"], "seed": 5}),
        content_type="application/json",
    )
    game_id = resp.get_json()["game_id"]

    # From engine: gather indices of all available nodes (count should be 54 in standard board)
    game = routes.GAMES[game_id]
    available_node_indices = {int(n.index) for n in game.board.nodes if n.available}
    # Each node appears once; sanity check count
    assert len(available_node_indices) == len(game.board.node_dict) == 54

    # From API state: gather indices offered as BUILD_SETTLEMENT actions
    state = client.get(f"/api/games/{game_id}/states/latest").get_json()
    action_node_indices = {
        int(a[2]) for a in state["current_playable_actions"] if a[1] == "BUILD_SETTLEMENT"
    }

    assert action_node_indices == available_node_indices


