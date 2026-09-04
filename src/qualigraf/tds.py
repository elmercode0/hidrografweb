"""US2 — Sólidos Totais Dissolvidos (STD) + classificação CONAMA 357/2005 (T012)."""

from __future__ import annotations

from .constants import TDS_CLASSES, TDS_FACTOR
from .io import DataError
from .models import SampleSet, TDSResult, WaterSample


def classify_tds(tds: float, classes=TDS_CLASSES) -> str:
    for name, upper in classes:
        if tds <= upper:
            return name
    return classes[-1][0]


def tds_sample(s: WaterSample, factor: float = TDS_FACTOR) -> TDSResult:
    if s.tds is not None:
        tds, source, ec = s.tds, "measured", s.ec
    elif s.ec is not None:
        tds, source, ec = s.ec * factor, "estimated", s.ec
    else:
        raise DataError(f"análise 'tds' requer 'tds' ou 'ec' (ausente na amostra {s.label})")

    return TDSResult(
        label=s.label,
        tds=round(tds, 2),
        source=source,
        ec=ec,
        factor=factor,
        conama_class=classify_tds(tds),
    )


def total_dissolved_solids(samples: SampleSet, factor: float = TDS_FACTOR) -> list[TDSResult]:
    return [tds_sample(s, factor=factor) for s in samples]
