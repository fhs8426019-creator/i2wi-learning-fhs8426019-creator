"""文字のテトリスの盤面とブロック（標準ライブラリだけ使用）。"""

# 種類ごとの、箱の中の4マスの位置 (行, 列)
SHAPES = {
    "I": [(1, 0), (1, 1), (1, 2), (1, 3)],
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "T": [(0, 1), (1, 0), (1, 1), (1, 2)],
    "S": [(0, 1), (0, 2), (1, 0), (1, 1)],
    "Z": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "J": [(0, 0), (1, 0), (1, 1), (1, 2)],
    "L": [(0, 2), (1, 0), (1, 1), (1, 2)],
}

# 回すときに使う箱の大きさ
BOX_SIZES = {"I": 4, "O": 2}
DEFAULT_BOX_SIZE = 3


class Board:
    """固定したマスと、いま落ちているブロックを持つ盤面。"""

    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]
        self.lines = 0
        self.game_over = False
        # 落ちているブロック: 箱の中のマス・箱の大きさ・箱の左上の位置
        self.cells = None
        self.size = 0
        self.top = 0
        self.left = 0

    def _positions(self, cells, top, left):
        """箱の中のマスを、盤面上の (行, 列) に直す。"""
        return [(top + r, left + c) for r, c in cells]

    def _fits(self, positions):
        """すべてのマスが盤面の中にあり、固定したマスと重ならなければ True。"""
        for r, c in positions:
            if not (0 <= r < self.height and 0 <= c < self.width):
                return False
            if self.grid[r][c] != 0:
                return False
        return True

    def spawn(self, kind):
        """kind のブロックを上端の中央あたりに出す。出せなければゲームオーバー。"""
        cells = list(SHAPES[kind])
        size = BOX_SIZES.get(kind, DEFAULT_BOX_SIZE)
        top = -min(r for r, c in cells)  # いちばん上のマスが行 0 に来るようにする
        left = (self.width - size) // 2
        if not self._fits(self._positions(cells, top, left)):
            self.cells = None
            self.game_over = True
            return False
        self.cells = cells
        self.size = size
        self.top = top
        self.left = left
        return True

    def piece_cells(self):
        """落ちているブロックのマスの set。無ければ空の set。"""
        if self.cells is None:
            return set()
        return set(self._positions(self.cells, self.top, self.left))

    def move(self, dx):
        """左右に dx マス動かす。動かせたら True。"""
        if self.cells is None:
            return False
        if not self._fits(self._positions(self.cells, self.top, self.left + dx)):
            return False
        self.left += dx
        return True

    def rotate(self):
        """箱の中で時計回りに90度回す: (行, 列) → (列, 箱の大きさ − 1 − 行)。回せたら True。"""
        if self.cells is None:
            return False
        rotated = [(c, self.size - 1 - r) for r, c in self.cells]
        if not self._fits(self._positions(rotated, self.top, self.left)):
            return False
        self.cells = rotated
        return True

    def step(self):
        """1段下げる。下げられなければ固定して行を消し、False を返す。"""
        if self.cells is None:
            return False
        if self._fits(self._positions(self.cells, self.top + 1, self.left)):
            self.top += 1
            return True
        self._lock()
        return False

    def hard_drop(self):
        """下げられなくなるまで下げて、固定する。"""
        while self.step():
            pass

    def _lock(self):
        """落ちているブロックを grid に書き込み、そろった行を消す。"""
        for r, c in self.piece_cells():
            self.grid[r][c] = 1
        self.cells = None
        remaining = [row for row in self.grid if not all(row)]
        cleared = self.height - len(remaining)
        self.grid = [[0] * self.width for _ in range(cleared)] + remaining
        self.lines += cleared

    def render(self):
        """固定したマスは #、落ちているブロックは @、空きは . の文字で返す。"""
        falling = self.piece_cells()
        rows = []
        for r in range(self.height):
            row = ""
            for c in range(self.width):
                if (r, c) in falling:
                    row += "@"
                elif self.grid[r][c]:
                    row += "#"
                else:
                    row += "."
            rows.append(row)
        return "\n".join(rows)
