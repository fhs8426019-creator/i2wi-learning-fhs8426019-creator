"""ターミナルで遊べる文字のテトリス（標準ライブラリだけ使用）。

操作: a=左  d=右  s=1段下げる  w=回す  スペース=一気に落とす  q=終了
"""
import contextlib
import os
import random
import sys
import time

ROWS = 20
COLS = 10
FALL_INTERVAL = 0.5  # 自動で1段落ちる間隔（秒）

# 種類ごとの (箱の大きさ, 箱の中のマスの (行, 列))
SHAPES = {
    "I": (4, [(1, 0), (1, 1), (1, 2), (1, 3)]),
    "O": (2, [(0, 0), (0, 1), (1, 0), (1, 1)]),
    "T": (3, [(0, 1), (1, 0), (1, 1), (1, 2)]),
    "S": (3, [(0, 1), (0, 2), (1, 0), (1, 1)]),
    "Z": (3, [(0, 0), (0, 1), (1, 1), (1, 2)]),
    "J": (3, [(0, 0), (1, 0), (1, 1), (1, 2)]),
    "L": (3, [(0, 2), (1, 0), (1, 1), (1, 2)]),
}


class Piece:
    """落ちているブロック。箱の中のマスと、箱の左上の位置で持つ。"""

    def __init__(self, kind):
        self.kind = kind
        self.size, cells = SHAPES[kind]
        self.cells = list(cells)
        self.top = 0
        self.left = (COLS - self.size) // 2

    def positions(self, cells=None, top=None, left=None):
        """盤面上の (行, 列) の一覧を返す。引数を渡すと、その状態で計算する。"""
        cells = self.cells if cells is None else cells
        top = self.top if top is None else top
        left = self.left if left is None else left
        return [(top + r, left + c) for r, c in cells]


def new_grid():
    return [[0] * COLS for _ in range(ROWS)]


def can_place(grid, positions):
    """すべてのマスが盤面内で、固定ブロックと重ならなければ True。"""
    for r, c in positions:
        if not (0 <= r < ROWS and 0 <= c < COLS):
            return False
        if grid[r][c] != 0:
            return False
    return True


def try_move(grid, piece, dr, dc):
    """動かせるか確かめてから動かす。動かせたら True。"""
    moved = piece.positions(top=piece.top + dr, left=piece.left + dc)
    if not can_place(grid, moved):
        return False
    piece.top += dr
    piece.left += dc
    return True


def try_rotate(grid, piece):
    """箱の中で時計回りに回す: (行, 列) → (列, size-1-行)。回せたら True。"""
    rotated = [(c, piece.size - 1 - r) for r, c in piece.cells]
    if not can_place(grid, piece.positions(cells=rotated)):
        return False
    piece.cells = rotated
    return True


def lock(grid, piece):
    """ブロックを固定し、grid に書き込む。"""
    for r, c in piece.positions():
        grid[r][c] = 1


def clear_lines(grid):
    """埋まった行を消し、消えた行数だけ空の行を上に足す。(新しい grid, 消えた行数) を返す。"""
    remaining = [row for row in grid if not all(row)]
    cleared = ROWS - len(remaining)
    return [[0] * COLS for _ in range(cleared)] + remaining, cleared


def render(grid, piece, lines):
    falling = set(piece.positions()) if piece else set()
    out = ["\x1b[H"]  # カーソルを左上に戻して上書きする
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            if (r, c) in falling:
                row.append("@")
            elif grid[r][c]:
                row.append("#")
            else:
                row.append(".")
        out.append("|" + "".join(row) + "|\n")
    out.append("+" + "-" * COLS + "+\n")
    out.append(f"消した行: {lines}\n")
    out.append("a=左 d=右 s=下 w=回す スペース=落とす q=終了\n")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


# --- キー入力（Windows とそれ以外で方法が違う） ---

if os.name == "nt":
    import msvcrt

    @contextlib.contextmanager
    def raw_mode():
        yield

    def get_key(timeout):
        """timeout 秒までキーを待つ。押されなければ None。"""
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):  # 矢印などの特殊キーは2文字目も読んで捨てる
                    msvcrt.getwch()
                    continue
                return ch
            time.sleep(0.01)
        return None

else:
    import select
    import termios
    import tty

    @contextlib.contextmanager
    def raw_mode():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def get_key(timeout):
        """timeout 秒までキーを待つ。押されなければ None。"""
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready:
            return sys.stdin.read(1)
        return None


def main():
    if os.name == "nt":
        os.system("")  # Windows のターミナルでエスケープシーケンスを有効にする
    grid = new_grid()
    piece = Piece(random.choice(list(SHAPES)))
    lines = 0
    sys.stdout.write("\x1b[2J\x1b[?25l")  # 画面を消し、カーソルを隠す

    def settle():
        """今のブロックを固定し、行を消して次のブロックを出す。置けなければ None。"""
        nonlocal grid, lines
        lock(grid, piece)
        grid, cleared = clear_lines(grid)
        lines += cleared
        nxt = Piece(random.choice(list(SHAPES)))
        return nxt if can_place(grid, nxt.positions()) else None

    try:
        with raw_mode():
            last_fall = time.monotonic()
            while piece is not None:
                render(grid, piece, lines)
                wait = max(0.0, last_fall + FALL_INTERVAL - time.monotonic())
                key = get_key(wait)

                if key is None or key.lower() == "s":
                    # 1段下げる。下げられなければ固定する
                    if not try_move(grid, piece, 1, 0):
                        piece = settle()
                    last_fall = time.monotonic()
                    continue

                key = key.lower()
                if key == "q":
                    break
                if key == "a":
                    try_move(grid, piece, 0, -1)
                elif key == "d":
                    try_move(grid, piece, 0, 1)
                elif key == "w":
                    try_rotate(grid, piece)
                elif key == " ":
                    while try_move(grid, piece, 1, 0):
                        pass
                    piece = settle()
                    last_fall = time.monotonic()

            render(grid, piece, lines)
            if piece is None:
                print("ゲームオーバー")
            else:
                print("終了しました")
    finally:
        sys.stdout.write("\x1b[?25h")  # カーソルを戻す
        sys.stdout.flush()


if __name__ == "__main__":
    main()
