import numpy as np

from catan import Board, Game, StructureAction, RoadAction, ActionType


def any_available_node_coords(board: Board):
    # Pick first available node's coordinates
    for node in board.nodes:
        if node.available:
            return node.coords
    raise AssertionError("No available node found")


def any_connected_edge_coords(board: Board, player: str):
    # Find an edge adjacent to player's placed settlement (first such)
    for edge in board.edges:
        # skip already taken edges
        if edge.player is not None:
            continue
        node_idxs = Board.edge_node_list[edge.index]
        nodes = [board.nodes[i] for i in node_idxs]
        # if one node belongs to player and other is not blocked, it should be valid
        if any(n.player == player for n in nodes):
            return edge.coords
    raise AssertionError("No connected edge found")


def test_step_flow_initial_structure_then_road_advances_turn():
    game = Game(players=["P1", "P2"], seed=1)
    assert game.cur_player == "P1"

    # First action: P1 builds settlement value 1
    ncoords_p1 = any_available_node_coords(game.board)
    ok = game.step(StructureAction(coords=ncoords_p1, value=1))
    assert ok is True

    # Still P1's turn for road in start phase
    assert game.cur_player == "P1"

    # Find an edge adjacent to P1 settlement
    ecoords = any_connected_edge_coords(game.board, "P1")
    ok = game.step(RoadAction(coords=ecoords))
    assert ok is True

    # After placing road, it advances to P2
    assert game.cur_player == "P2"

