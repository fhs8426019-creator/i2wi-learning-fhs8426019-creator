def solve(a, b, c):
    d = b * b - 4 * a * c
    if d < 0:
        re = -b / (2 * a)
        im = (-d) ** 0.5 / (2 * a)
        return [complex(re, im), complex(re, -im)]
    s = d ** 0.5
    return [(-b + s) / (2 * a), (-b - s) / (2 * a)]
