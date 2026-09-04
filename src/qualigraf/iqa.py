"""US4 — Índice de Qualidade da Água (IQA), produtório ponderado CETESB (T019)."""

from __future__ import annotations

from .constants import IQA_RANGES_CETESB, IQA_RANGES_IGAM, IQA_WEIGHTS
from .io import DataError
from .iqa_curves import qi as _qi
from .models import IQAResult, SampleSet, WaterSample


def _classify(iqa: float, ranges) -> str:
    """ranges: sequência (rótulo, limite_inferior_incl, limite_superior_excl)."""
    for label, lo, hi in ranges:
        if lo <= iqa < hi:
            return label
    return ranges[-1][0]


def iqa_sample(s: WaterSample, weights: dict[str, float] | None = None) -> IQAResult:
    """IQA = Π qi^wi sobre os 9 parâmetros. Erro se faltar qualquer um."""
    weights = weights or IQA_WEIGHTS

    missing = [p for p in weights if getattr(s, p, None) is None]
    if missing:
        raise DataError(
            f"IQA requer '{missing[0]}' (ausente na amostra {s.label}); "
            f"faltam: {', '.join(missing)}"
        )

    qi_values: dict[str, float] = {}
    iqa = 1.0
    for param, w in weights.items():
        q = _qi(param, float(getattr(s, param)))
        q = max(q, 1.0)  # evita 0^w e produto nulo; qi mínimo 1
        qi_values[param] = round(q, 2)
        iqa *= q ** w

    iqa = round(iqa, 2)
    return IQAResult(
        label=s.label,
        iqa=iqa,
        qi=qi_values,
        cetesb_class=_classify(iqa, IQA_RANGES_CETESB),
        igam_class=_classify(iqa, IQA_RANGES_IGAM),
    )


def water_quality_index(samples: SampleSet, **kw) -> list[IQAResult]:
    return [iqa_sample(s, **kw) for s in samples]
