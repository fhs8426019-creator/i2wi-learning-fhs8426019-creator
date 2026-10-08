import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from tetris import Piece, new_grid, try_move, try_rotate, lock, clear_lines, ROWS, COLS

def test_left_wall():
    grid = new_grid()
    p = Piece("T")
    for _ in range(20):
        try_move(grid, p, 0, -1)
    cols = [c for r, c in p.positions()]
    assert min(cols) == 0, f"左端が0でない: {min(cols)}"
    return "OK"

def test_rotate4():
    grid = new_grid()
    p = Piece("T")
    try_move(grid, p, 1, 0)  # 回せるように1段下げておく
    orig = sorted(p.positions())
    for _ in range(4):
        assert try_rotate(grid, p), "回転できなかった"
    assert sorted(p.positions()) == orig, f"4回回転後にずれた: {p.positions()}"
    return "OK"

def test_rotate_wall():
    grid = new_grid()
    p = Piece("I")
    try_move(grid, p, 2, 0)  # 縦にしても上にはみ出さないように下げておく
    for _ in range(20):
        try_move(grid, p, 0, -1)
    for _ in range(4):
        try_rotate(grid, p)
        cols = [c for r, c in p.positions()]
        assert min(cols) >= 0, f"回転後に左へはみ出た: {cols}"
        assert max(cols) <= COLS - 1, f"回転後に右へはみ出た: {cols}"
    return "OK"

def test_clear_line():
    grid = new_grid()
    p = Piece("O")  # 列4と列5を占める
    for c in range(COLS):
        if c not in (4, 5):
            grid[ROWS - 1][c] = 1
    while try_move(grid, p, 1, 0):
        pass
    lock(grid, p)  # 一番下の行がそろい、O の上半分が1つ上の行に残る
    grid, cleared = clear_lines(grid)
    assert cleared == 1, f"消えた行数が1でない: {cleared}"
    expected = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]
    assert grid[ROWS - 1] == expected, f"上の行が下がっていない: {grid[ROWS - 1]}"
    assert grid[ROWS - 2] == [0] * COLS, f"上の行が空になっていない: {grid[ROWS - 2]}"
    return "OK"

tests = [test_left_wall, test_rotate4, test_rotate_wall, test_clear_line]
for t in tests:
    try:
        print(f"{t.__name__}: {t()}")
    except Exception as e:
        print(f"{t.__name__}: NG — {e}")
