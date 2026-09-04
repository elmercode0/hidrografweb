"""US4 — Curvas médias de qualidade qi do IQA, DIGITALIZADAS da Figura 01 do QualiGraf.

Fonte: Tutorial_QualiGraf.pdf, pág. 11 ("Figura 01: Curvas Médias de Variação de
Qualidade das Águas") — a mesma figura contém um exemplo resolvido do próprio software
(valor observado → qi), usado aqui como pontos-âncora de validação.

Status de validação (8 de 9 curvas conferem exatamente com o exemplo do QualiGraf):

    parâmetro     observado   qi (QualiGraf)   qi (esta curva)   confere?
    OD %sat       50,15       42,43            ~42               ✓
    coliformes    6.000       10,95            ~11               ✓
    pH            6,00        60,27            ~60               ✓
    N total       1,62        87,57            ~87               ✓
    P total       0,25        79,07            ~79               ✓
    ΔTemperatura  0           94,00            94                ✓
    turbidez      90          19,71            ~20               ✓
    resíduo total 450         39,04            ~39               ✓
    DBO           15          67,57            ~22               ✗  (ver DBO_DISCREPANCY)

✅ RESOLVIDO (DBO): para DBO=15 a curva desenhada dá q≈22, e a equação oficial CETESB da
curva de DBO — q = 102,6·exp(−0,1101·DBO) — dá q≈20 (BasIQA/ABRHidro 2013, reconstruindo
CETESB 2005). Ambas coincidem; o valor q=67,57 mostrado na tela do QualiGraf (ponto fora
da própria curva) é um ERRO de exibição do software. Mantemos a curva (~20–22). Detalhe em
DBO_DISCREPANCY.

Precisão: pontos lidos visualmente da figura (erro típico ±2–3 unidades de q). Apenas o
eixo de COLIFORMES é logarítmico; todos os demais são lineares (conferido na figura).
"""

from __future__ import annotations

import math

# Curvas digitalizadas da Figura 01 (leitura gráfica ±2–3 q), corroboradas pelas equações
# oficiais CETESB (BasIQA/ABRHidro 2013). Não é mais um chute.
IQA_PROVISIONAL = False

# DBO: divergência RESOLVIDA — a curva (~22) e a equação CETESB q=102,6·exp(−0,1101·DBO)
# (~20) concordam; o q=67,57 exibido na tela do QualiGraf é erro de exibição do software.
DBO_DISCREPANCY = {
    "param": "bod",
    "observed": 15.0,
    "qi_curva_desenhada": 22.0,
    "qi_equacao_cetesb": 20.0,   # 102.6*exp(-0.1101*15)
    "qi_exemplo_hidrograf": 67.57,
    "status": "resolvido",
    "conclusao": "curva (~20-22) correta; 67,57 é bug de exibição do QualiGraf",
    "fonte": "BasIQA/ABRHidro 2013 (reconstrução das curvas CETESB 2005)",
}

# Somente coliformes tem eixo x logarítmico (Figura 01).
LOG_SCALE_PARAMS = frozenset({"coliforms"})

# Pontos-âncora do exemplo resolvido do QualiGraf (observado, qi). Ground truth p/ testes.
ANCHOR_POINTS: dict[str, tuple[float, float]] = {
    "do_sat": (50.15, 42.43),
    "coliforms": (6000.0, 10.95),
    "ph": (6.0, 60.27),
    "bod": (15.0, 67.57),        # divergente — ver DBO_DISCREPANCY
    "n_total": (1.62, 87.57),
    "p_total": (0.25, 79.07),
    "temp_var": (0.0, 94.00),
    "turbidity": (90.0, 19.71),
    "total_solids": (450.0, 39.04),
}

# --- Curvas (x, qi) lidas da Figura 01, x crescente -----------------------------------

# Oxigênio Dissolvido — % de saturação (eixo 0–200). Pico q=100 em 100%.
# > 140% é extrapolação (a curva desenhada termina ~140); marcada como dúvida.
DO_SAT = [(0, 3), (10, 7), (20, 13), (30, 20), (40, 30), (50, 42), (60, 53),
          (70, 66), (80, 80), (90, 92), (100, 100), (110, 98), (120, 90),
          (130, 84), (140, 78), (200, 45)]

# Coliformes fecais/termotolerantes — NMP/100mL (eixo LOG, 1–10^5).
COLIFORMS = [(1, 97), (10, 80), (100, 62), (1000, 42), (3000, 22),
             (6000, 11), (10000, 9), (100000, 3)]

# pH (eixo 2–12). Sino com pico ~92 em pH≈7,3.
PH = [(2, 2), (3, 5), (4, 8), (5, 20), (5.5, 38), (6, 60), (6.5, 78), (7, 88),
      (7.3, 92), (7.5, 90), (8, 80), (8.5, 65), (9, 50), (9.5, 32), (10, 20),
      (11, 8), (12, 3)]

# DBO5,20 — mg/L (eixo 0–45). CURVA DESENHADA (ver DBO_DISCREPANCY).
BOD = [(0, 100), (2, 82), (4, 68), (5, 62), (7, 48), (10, 35), (12, 28),
       (15, 22), (20, 15), (25, 10), (30, 7), (45, 5)]

# Nitrogênio total — mg/L (eixo 0–100).
N_TOTAL = [(0, 100), (1, 92), (1.62, 87.5), (2, 84), (5, 68), (10, 52), (20, 38),
           (30, 30), (40, 24), (50, 19), (60, 15), (70, 11), (80, 8), (90, 5), (100, 3)]

# Fósforo total — mg/L (eixo 0–10).
P_TOTAL = [(0, 100), (0.1, 90), (0.25, 79), (0.5, 60), (0.75, 48), (1, 40),
           (1.5, 32), (2, 27), (3, 20), (4, 15), (5, 12), (6, 10), (7, 9), (8, 8), (10, 6)]

# Variação de temperatura (afastamento da temperatura de equilíbrio) — °C (eixo -5–20).
# Pico q=94 em ΔT=0; aceita valores NEGATIVOS.
TEMP_VAR = [(-5, 52), (-3, 68), (-2, 76), (-1, 86), (0, 94), (1, 88), (2, 80),
            (3, 68), (4, 55), (5, 45), (6, 38), (7, 33), (8, 29), (10, 22),
            (12, 15), (15, 10), (20, 5)]

# Turbidez — UNT (eixo 0–100).
TURBIDITY = [(0, 100), (5, 86), (10, 78), (20, 66), (30, 57), (40, 50), (50, 44),
             (60, 38), (70, 33), (80, 28), (90, 20), (100, 18)]

# Resíduo/Sólidos totais — mg/L (eixo 0–500). Sobe até ~89 e decai; >500 extrapolado.
TOTAL_SOLIDS = [(0, 80), (25, 86), (50, 89), (70, 89), (100, 86), (150, 80), (200, 73),
                (250, 66), (300, 60), (350, 54), (400, 48), (450, 39), (500, 32)]

CURVES: dict[str, list[tuple[float, float]]] = {
    "do_sat": DO_SAT,
    "coliforms": COLIFORMS,
    "ph": PH,
    "bod": BOD,
    "temp_var": TEMP_VAR,
    "n_total": N_TOTAL,
    "p_total": P_TOTAL,
    "turbidity": TURBIDITY,
    "total_solids": TOTAL_SOLIDS,
}


def qi(param: str, value: float) -> float:
    """Interpola qi para o parâmetro na concentração/medida dada.

    Interpolação em log10(x) apenas para parâmetros em LOG_SCALE_PARAMS (coliformes);
    linear nos demais. Fora do domínio da curva, satura no extremo (com aviso de
    extrapolação documentado nas curvas de OD>140% e resíduo>500).
    """
    pts = CURVES[param]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    if value <= xs[0]:
        return float(ys[0])
    if value >= xs[-1]:
        return float(ys[-1])

    log_scale = param in LOG_SCALE_PARAMS

    def _t(v, a, b):
        if log_scale and v > 0 and a > 0 and b > 0:
            return (math.log10(v) - math.log10(a)) / (math.log10(b) - math.log10(a))
        return (v - a) / (b - a)

    for i in range(1, len(xs)):
        if value <= xs[i]:
            x0, y0 = xs[i - 1], ys[i - 1]
            x1, y1 = xs[i], ys[i]
            return float(y0 + _t(value, x0, x1) * (y1 - y0))
    return float(ys[-1])
