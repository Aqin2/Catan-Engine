from catan import Board, Game, StructureAction, RoadAction


def test_cannot_place_road_disconnected():
    game = Game(players=["A", "B"], seed=5)

    # A places a settlement
    a_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=a_node.coords, value=1))

    # It's A's road turn now (initial placement)
    # Find an edge that is NOT adjacent to A's settlement (disconnected)
    disconnected_edge = next(
        e for e in game.board.edges
        if e.player is None and all(game.board.nodes[i].player != "A" for i in Board.edge_node_list[e.index])
    )

    assert game.step(RoadAction(coords=disconnected_edge.coords)) is False


def test_can_place_connected_road():
    game = Game(players=["A", "B"], seed=6)

    # A places a settlement
    a_node = next(n for n in game.board.nodes if n.available)
    assert game.step(StructureAction(coords=a_node.coords, value=1))

    # Choose an edge adjacent to A's settlement, should be valid
    ecoords = next(
        e.coords for e in game.board.edges
        if any(idx == a_node.index for idx in Board.edge_node_list[e.index]) and e.player is None
    )
    assert game.step(RoadAction(coords=ecoords)) is True

