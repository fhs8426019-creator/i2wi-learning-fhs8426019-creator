from tetris import Board, SHAPES

results = []


def check(label, ok, detail=""):
    results.append(ok)
    print(f"{label}: {'OK' if ok else 'NG'}")
    if not ok and detail:
        print("  " + detail)


def filled(b):
    return sum(sum(row) for row in b.grid)


# 1. 空の盤面
b = Board()
check("1. 空の盤面は 20行×10列で、何も無い",
      len(b.grid) == 20 and all(len(row) == 10 for row in b.grid) and filled(b) == 0
      and b.lines == 0 and not b.game_over)

# 2. 出したブロック
ok = True
for kind in SHAPES:
    b = Board()
    cells = b.piece_cells() if b.spawn(kind) else set()
    if len(cells) != 4 or min(r for r, _ in cells) != 0:
        ok = False
check("2. 7種とも、4マスで上端に出る", ok)

# 3. 左の壁
b = Board()
b.spawn("T")
start = min(c for _, c in b.piece_cells())
moves = [b.move(-1) for _ in range(20)]
check("3. 左に動かし続けると列 0 で止まり、それ以上は False",
      min(c for _, c in b.piece_cells()) == 0 and moves.count(True) == start and moves[-1] is False,
      f"True の回数 {moves.count(True)}、動く前の左端 {start}")

# 4. 4回回すと元に戻る
ok = True
for kind in SHAPES:
    b = Board()
    b.spawn(kind)
    b.step()
    b.step()
    before = b.piece_cells()
    for _ in range(4):
        b.rotate()
        if len(b.piece_cells()) != 4:
            ok = False
    if b.piece_cells() != before:
        ok = False
check("4. 7種とも、4回回すと元の形と位置に戻る", ok)

# 5. T は回すと形が変わる
b = Board()
b.spawn("T")
b.step()
b.step()
before = b.piece_cells()
b.rotate()
check("5. T を1回回すと、マスの並びが変わる", b.piece_cells() != before)

# 6. 壁際で回しても、盤面からはみ出さない
def wall_rotation_ok(kind, dx, pre):
    b = Board()
    b.spawn(kind)
    b.step()
    b.step()
    for _ in range(pre):
        b.rotate()
    for _ in range(20):
        b.move(dx)
    for _ in range(4):
        before = b.piece_cells()
        turned = b.rotate()
        cells = b.piece_cells()
        if any(not (0 <= r < 20 and 0 <= c < 10) for r, c in cells):
            return False
        if not turned and cells != before:
            return False
    return True


check("6. 壁際で回しても、はみ出さない（回せないときは動かない）",
      all(wall_rotation_ok(k, dx, pre) for k in SHAPES for dx in (-1, 1) for pre in range(4)))

# 7. 一気に落とすと最下段に着く
b = Board()
b.spawn("O")
b.hard_drop()
bottom = [r for r in range(20) if any(b.grid[r])]
check("7. O を一気に落とすと、最下段の2行に固定される",
      filled(b) == 4 and bottom == [18, 19] and b.piece_cells() == set(),
      f"埋まった行 {bottom}")

# 8. 積んだブロックの上に止まる
b = Board()
b.grid[19] = [1] * 9 + [0]
b.spawn("O")
b.hard_drop()
check("8. 積んだ段の上で止まる", sum(b.grid[18]) == 2 and sum(b.grid[17]) == 2 and b.lines == 0)


def vertical_i_to_left(b):
    b.spawn("I")
    b.step()
    b.step()
    b.rotate()
    for _ in range(20):
        b.move(-1)
    return {c for _, c in b.piece_cells()} == {0}


# 9. 1行消えて、上の段が1つ下がる
b = Board()
b.grid[19] = [0] + [1] * 9
b.grid[18][5] = 1
placed = vertical_i_to_left(b)
b.hard_drop()
check("9. 1行そろうと消え、上の段が1つ下がる",
      placed and b.lines == 1 and b.grid[19][0] == 1 and b.grid[19][5] == 1
      and b.grid[18][5] == 0 and filled(b) == 4,
      f"lines={b.lines}\n" + b.render())

# 10. 4行同時に消える
b = Board()
for r in range(16, 20):
    b.grid[r] = [0] + [1] * 9
placed = vertical_i_to_left(b)
b.hard_drop()
check("10. 4行そろうと4行とも消える", placed and b.lines == 4 and filled(b) == 0,
      f"lines={b.lines}")

# 11. 積み上がるとゲームオーバー
b = Board()
b.grid[0] = [1] * 10
b.grid[1] = [1] * 10
check("11. 出す場所が埋まっていると、spawn は False でゲームオーバー",
      b.spawn("T") is False and b.game_over is True)

print(f"\n{results.count(True)} / {len(results)} 項目が OK")
