def solve(a, b, c):
    """2次方程式 ax^2 + bx + c = 0 の解をリストで返す。"""
    if a == 0:
        if b != 0:
            # 1次方程式 bx + c = 0
            return [-c / b]
        if c != 0:
            # 解なし
            return []
        # a, b, c がすべて 0
        raise ValueError("すべての x が解です")

    d = b * b - 4 * a * c

    if d > 0:
        root = d ** 0.5
        # 大きいほうの解: -b と符号をそろえて足し算にし、桁落ちを避ける
        if b >= 0:
            big = (-b - root) / (2 * a)
        else:
            big = (-b + root) / (2 * a)
        # 小さいほうの解: 解と係数の関係（2つの解の積 = c/a）から求める
        small = c / (a * big)
        return [big, small]

    if d == 0:
        return [-b / (2 * a)]

    # 判別式が負: 負の数に ** 0.5 を使わず、実部と虚部を別々に計算する
    real = -b / (2 * a)
    imag = (-d) ** 0.5 / (2 * a)
    return [complex(real, imag), complex(real, -imag)]


if __name__ == "__main__":
    cases = [
        (1, -3, 2),
        (2, -6, 4),
        (1, 2, 1),
        (1, 0, 1),
        (1, 2, 5),
        (0, 2, -4),
        (0, 0, 1),
        (0, 0, 0),
        (1, -100000000, 1),
    ]
    for a, b, c in cases:
        try:
            print(f"{a}, {b}, {c} -> {solve(a, b, c)}")
        except ValueError as e:
            print(f"{a}, {b}, {c} -> ValueError: {e}")
