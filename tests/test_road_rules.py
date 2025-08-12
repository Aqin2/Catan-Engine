from catan import Board, Game, StructureAction, RoadAction


def test_cannot_place_road_disconnected():
    game = Game(players=["A", "B"], seed=5)

    # A places a settlement
    a_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=a_node.coords, value=1))

    # B places a settlement (advance)
    b_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=b_node.coords, value=1))

    # It's A's road turn now
    # Find an edge that is NOT adjacent to A's settlement and should be disconnected
    disconnected_edge = next(
        e for e in game.board.edges
        if e.player is None and all(game.board.nodes[i].player != "A" for i in Board.edge_node_list[e.index])
    )

    assert game.step(RoadAction(coords=disconnected_edge.coords)) is False


def test_cannot_place_through_opponent_settlement():
    game = Game(players=["A", "B"], seed=9)

    # A settlement
    a_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=a_node.coords, value=1))
    # B settlement
    b_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=b_node.coords, value=1))

    # A road turn: pick an edge adjacent to B's settlement only; should be blocked
    blocking_edge = next(
        e for e in game.board.edges
        if e.player is None and any(game.board.nodes[i] is b_node for i in Board.edge_node_list[e.index])
    )
    assert game.step(RoadAction(coords=blocking_edge.coords)) is False

