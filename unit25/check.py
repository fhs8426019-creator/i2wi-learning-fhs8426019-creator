from quadratic import solve

cases = [
    (1, -3, 2),
    (2, -6, 4),
    (1, 2, 1),
    (1, 0, 1),
    (1, 2, 5),
    (1, -100000000, 1),
]

for a, b, c in cases:
    for x in solve(a, b, c):
        residual = a * x * x + b * x + c
        scale = abs(a * x * x) + abs(b * x) + abs(c)
        ratio = abs(residual) / scale
        mark = "OK" if ratio < 1e-12 else "NG"
        print(f"({a}, {b}, {c})  x = {x}  相対誤差 {ratio:.1e}  {mark}")
