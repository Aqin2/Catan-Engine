import numpy as np

from catan import Board, Resource


def test_board_has_19_tiles_and_one_desert():
    board = Board(seed=42)

    assert len(board.tiles) == 19

    desert_tiles = [t for t in board.tiles if t.resource == Resource.DESERT]
    assert len(desert_tiles) == 1
    assert desert_tiles[0].number == -1


def test_numbers_length_and_values_with_desert_inserted():
    board = Board(seed=7)
    numbers = [t.number for t in board.tiles]

    assert len(numbers) == 19
    # One desert marked with -1, others in 2..12 excluding 7
    assert numbers.count(-1) == 1
    for n in numbers:
        if n != -1:
            assert n in {2, 3, 4, 5, 6, 8, 9, 10, 11, 12}


def test_ports_distribution_and_dirs():
    board = Board(seed=123)
    # 9 ports expected
    assert len(board.ports) == 9
    # Every port should have 2 directions
    for p in board.ports:
        assert hasattr(p, "dirs")
        assert len(p.dirs) == 2

