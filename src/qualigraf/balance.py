"""US1 — Balanço iônico e erro prático Ep% (Custódio & Llamas, 1983) (T009).

Ep(%) = 100 · (Σânions − Σcátions) / [½ · (Σcátions + Σânions)]   (meq/L)

Aceitação por duas técnicas (mesma fórmula, tabelas diferentes), como no QualiGraf:
  • por CE  — Custódio & Llamas (1983): tolerância função da condutividade elétrica.
  • por soma — Logan (1965): tolerância função da soma de ânions/cátions.
"""

from __future__ import annotations

from .constants import BALANCE_TOLERANCE_CE, BALANCE_TOLERANCE_SUM
from .models import BalanceResult, SampleSet, WaterSample

# Íons maiores esperados numa análise completa; ausência torna o Ep% pouco confiável.
_MAJOR_IONS = ("ca", "mg", "na", "cl", "so4", "hco3")


def practical_error(sum_cat: float, sum_an: float) -> float:
    """Erro prático Ep% (Custódio & Llamas, 1983). Sinal: + indica excesso de ânions."""
    denom = 0.5 * (sum_cat + sum_an)
    if denom == 0:
        return 0.0
    return 100.0 * (sum_an - sum_cat) / denom


def tolerance_ce(ce: float, table=BALANCE_TOLERANCE_CE) -> float:
    """Erro máximo admissível pela CE (µS/cm), interpolado (Custódio & Llamas)."""
    if ce <= table[0][0]:
        return table[0][1]
    if ce >= table[-1][0]:
        return table[-1][1]
    for i in range(1, len(table)):
        x0, y0 = table[i - 1]
        x1, y1 = table[i]
        if ce <= x1:
            return y0 + (ce - x0) / (x1 - x0) * (y1 - y0)
    return table[-1][1]


def tolerance_sum(sum_meq: float, table=BALANCE_TOLERANCE_SUM) -> float:
    """Erro máximo admissível pela soma de íons (meq/L), por faixa (Logan, 1965)."""
    for upper, tol in table:
        if sum_meq <= upper:
            return tol
    return table[-1][1]


def balance_sample(
    s: WaterSample,
    weights: dict[str, float] | None = None,
) -> BalanceResult:
    cations = s.cations_meq(weights)
    anions = s.anions_meq(weights)
    sum_cat = sum(cations.values())
    sum_an = sum(anions.values())

    ep = practical_error(sum_cat, sum_an)

    tol_ce = tolerance_ce(s.ec) if s.ec is not None else None
    # Logan usa a soma de ânions (ou cátions) — usamos a maior das duas.
    tol_logan = tolerance_sum(max(sum_cat, sum_an))

    missing = tuple(i for i in _MAJOR_IONS if not s.has(i))

    return BalanceResult(
        label=s.label,
        cations_meq={k: round(v, 4) for k, v in cations.items()},
        anions_meq={k: round(v, 4) for k, v in anions.items()},
        sum_cations=round(sum_cat, 4),
        sum_anions=round(sum_an, 4),
        ep=round(ep, 3),
        tol_ce=round(tol_ce, 2) if tol_ce is not None else None,
        tol_logan=round(tol_logan, 2),
        acceptable_ce=(abs(ep) <= tol_ce) if tol_ce is not None else None,
        acceptable_logan=abs(ep) <= tol_logan,
        complete=not missing,
        missing_major=missing,
    )


def ionic_balance(samples: SampleSet, **kw) -> list[BalanceResult]:
    return [balance_sample(s, **kw) for s in samples]
