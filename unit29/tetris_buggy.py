# 文字で遊ぶテトリスの盤面とブロック。標準ライブラリだけで書く。
# 盤面の座標は (行, 列)。行は上が 0、列は左が 0。

SHAPES = {
    "I": [(0, 0), (0, 1), (0, 2), (0, 3)],
    "O": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "T": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "S": [(0, 1), (0, 2), (1, 0), (1, 1)],
    "Z": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "J": [(0, 0), (1, 0), (1, 1), (1, 2)],
    "L": [(0, 2), (1, 0), (1, 1), (1, 2)],
}


class Board:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]
        self.lines = 0
        self.game_over = False
        self.kind = None
        self.turns = 0
        self.top = 0
        self.left = 0

    def _box(self):
        return {"I": 4, "O": 2}.get(self.kind, 3)

    def _cells(self, turns, top, left):
        size = self._box()
        cells = SHAPES[self.kind]
        for _ in range(turns % 4):
            cells = [(c, size - 1 - r) for r, c in cells]
        return {(top + r, left + c) for r, c in cells}

    def piece_cells(self):
        if self.kind is None:
            return set()
        return self._cells(self.turns, self.top, self.left)

    def _fits(self, cells):
        for r, c in cells:
            if not (0 <= r < self.height and 0 <= c < self.width):
                return False
            if self.grid[r][c]:
                return False
        return True

    def spawn(self, kind):
        self.kind, self.turns = kind, 0
        self.top = 0
        self.left = (self.width - self._box()) // 2
        if not self._fits(self.piece_cells()):
            self.game_over = True
            self.kind = None
            return False
        return True

    def _try(self, turns, top, left):
        if self.kind is None or not self._fits(self._cells(turns, top, left)):
            return False
        self.turns, self.top, self.left = turns % 4, top, left
        return True

    def move(self, dx):
        return self._try(self.turns, self.top, self.left + dx)

    def rotate(self):
        return self._try(self.turns + 1, self.top, self.left)

    def step(self):
        if self._try(self.turns, self.top + 1, self.left):
            return True
        self._lock()
        return False

    def hard_drop(self):
        while self.step():
            pass

    def _lock(self):
        for r, c in self.piece_cells():
            self.grid[r][c] = 1
        self.kind = None
        remaining = [row for row in self.grid if not all(row)]
        cleared = self.height - len(remaining)
        self.grid = [[0] * self.width for _ in range(cleared)] + remaining
        self.lines += cleared

    def render(self):
        cells = self.piece_cells()
        rows = []
        for r in range(self.height):
            line = ""
            for c in range(self.width):
                if (r, c) in cells:
                    line += "@"
                elif self.grid[r][c]:
                    line += "#"
                else:
                    line += "."
            rows.append(line)
        return "\n".join(rows)
