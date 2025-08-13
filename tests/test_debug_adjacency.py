import json

from catan import Board


def test_print_node_adjacency():
    """Debug helper: print each node and its adjacent node indices.

    Run with: `python -m pytest -q -s tests/test_debug_adjacency.py`
    """
    board = Board(seed=1)

    # Sanity: standard board should have 54 unique nodes
    assert len(board.node_dict) == 54

    for node in board.nodes:
        adj_nodes = Board.node_node_list[node.index]
        data = {
            "node_index": int(node.index),
            "coords": [int(node.coords[0]), int(node.coords[1]), int(node.coords[2])],
            "adj_nodes": list(map(int, adj_nodes)),
        }
        print(json.dumps(data))



