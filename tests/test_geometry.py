import math

from hidrograf.geometry import normalize3, ternary_to_xy

_H = math.sqrt(3) / 2.0


def test_vertices():
    # a=100% -> canto inferior esquerdo (0,0)
    assert ternary_to_xy(1, 0, 0) == (0.0, 0.0)
    # b=100% -> canto inferior direito (1,0)
    assert ternary_to_xy(0, 1, 0) == (1.0, 0.0)
    # c=100% -> topo (0.5, H)
    x, y = ternary_to_xy(0, 0, 1)
    assert abs(x - 0.5) < 1e-9 and abs(y - _H) < 1e-9


def test_centroid():
    x, y = ternary_to_xy(1, 1, 1)
    assert abs(x - 0.5) < 1e-9
    assert abs(y - _H / 3) < 1e-9


def test_normalize():
    a, b, c = normalize3(2, 2, 1)
    assert abs(a + b + c - 100.0) < 1e-9
