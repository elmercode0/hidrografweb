"""US5 — Coordenadas ternárias para os diagramas de Piper e Durov (T022).

Convenção do triângulo equilátero com base [0,1] no eixo x e altura sqrt(3)/2:
- vértice inferior-esquerdo (a=100%) em (0, 0)
- vértice inferior-direito (b=100%) em (1, 0)
- vértice do topo (c=100%) em (0.5, sqrt(3)/2)
"""

from __future__ import annotations

import math

_H = math.sqrt(3) / 2.0


def ternary_to_xy(a: float, b: float, c: float) -> tuple[float, float]:
    """Converte proporções (a,b,c) — quaisquer, serão normalizadas — em (x,y).

    a = canto inferior-esquerdo, b = inferior-direito, c = topo.
    """
    total = a + b + c
    if total <= 0:
        raise ValueError("soma das componentes ternárias deve ser > 0")
    a, b, c = a / total, b / total, c / total
    x = b + c / 2.0
    y = c * _H
    return x, y


def normalize3(a: float, b: float, c: float) -> tuple[float, float, float]:
    total = a + b + c
    if total <= 0:
        return 0.0, 0.0, 0.0
    return 100.0 * a / total, 100.0 * b / total, 100.0 * c / total
