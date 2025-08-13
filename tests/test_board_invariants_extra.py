from catan import Board


def test_edges_have_two_nodes_and_node_degrees_valid():
    board = Board(seed=123)

    # Every edge must connect exactly two nodes
    for eidx, node_indices in enumerate(Board.edge_node_list):
        assert len(node_indices) == 2, f"edge {eidx} has {len(node_indices)} node(s)"

    # Every node must connect to 2 or 3 edges, and 2 or 3 neighbor nodes
    for nidx, edges in enumerate(Board.node_edge_list):
        assert 2 <= len(edges) <= 3
    for nidx, neighbors in enumerate(Board.node_node_list):
        assert 2 <= len(neighbors) <= 3


