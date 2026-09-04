"""Conversões mg/L <-> meq/L (T006)."""

from __future__ import annotations

from .constants import EQUIVALENT_WEIGHTS


def to_meq(mg_per_l: float, ion: str, weights: dict[str, float] | None = None) -> float:
    """Converte mg/L -> meq/L para o íon dado."""
    weights = weights or EQUIVALENT_WEIGHTS
    ion = ion.lower()
    if ion not in weights:
        raise KeyError(f"peso equivalente desconhecido para o íon '{ion}'")
    return mg_per_l / weights[ion]


def to_mg(meq_per_l: float, ion: str, weights: dict[str, float] | None = None) -> float:
    """Converte meq/L -> mg/L para o íon dado."""
    weights = weights or EQUIVALENT_WEIGHTS
    ion = ion.lower()
    if ion not in weights:
        raise KeyError(f"peso equivalente desconhecido para o íon '{ion}'")
    return meq_per_l * weights[ion]


def do_saturation_mgl(temp_c: float, altitude_m: float = 0.0) -> float:
    """Concentração de saturação de OD (mg/L) em função da temperatura e altitude.

    Solubilidade ao nível do mar: aproximação polinomial da APHA/Standard Methods
    (Elmore & Hayes), válida ~0–40 °C. Correção de altitude por fator barométrico
    simplificado (≈ água doce). Base para converter OD medido (mg/L) → % de saturação,
    parâmetro exigido pelo IQA (o QualiGraf faz isso com o botão "Alterar Altitude").
    """
    t = temp_c
    cs = 14.652 - 0.41022 * t + 0.0079910 * t * t - 0.000077774 * t * t * t
    # Correção de pressão/altitude (fator ≈ 1 − altitude/9450 m; APHA aprox.).
    factor = max(0.0, 1.0 - altitude_m / 9450.0)
    return cs * factor


def do_saturation_pct(od_mgl: float, temp_c: float, altitude_m: float = 0.0) -> float:
    """% de saturação de OD = 100 · OD(mg/L) / OD_saturação(T, altitude). Ver CETESB."""
    cs = do_saturation_mgl(temp_c, altitude_m)
    if cs <= 0:
        return 0.0
    return 100.0 * od_mgl / cs
