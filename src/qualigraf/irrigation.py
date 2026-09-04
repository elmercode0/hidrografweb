"""US3 — SAR e classificação USSL para irrigação (Richards, 1954) (T015)."""

from __future__ import annotations

import math

from .constants import USSL_C_THRESHOLDS, USSL_S_THRESHOLDS
from .models import SampleSet, SARResult, WaterSample


def sar_value(na_meq: float, ca_meq: float, mg_meq: float) -> float | None:
    """SAR = Na / sqrt((Ca + Mg) / 2), todos em meq/L. None se indefinido."""
    denom = (ca_meq + mg_meq) / 2.0
    if denom <= 0:
        return None
    return na_meq / math.sqrt(denom)


def _classify(value: float, thresholds) -> str:
    for label, upper in thresholds:
        if value < upper:
            return label
    return thresholds[-1][0]


def sar_sample(s: WaterSample, weights: dict[str, float] | None = None) -> SARResult:
    na = s.meq("na", weights) if s.has("na") else None
    ca = s.meq("ca", weights) if s.has("ca") else 0.0
    mg = s.meq("mg", weights) if s.has("mg") else 0.0

    sar = None if na is None else sar_value(na, ca or 0.0, mg or 0.0)
    s_class = _classify(sar, USSL_S_THRESHOLDS) if sar is not None else None
    c_class = _classify(s.ec, USSL_C_THRESHOLDS) if s.ec is not None else None
    ussl = f"{c_class}{s_class}" if (c_class and s_class) else None

    return SARResult(
        label=s.label,
        sar=round(sar, 3) if sar is not None else None,
        ec=s.ec,
        c_class=c_class,
        s_class=s_class,
        ussl_label=ussl,
    )


def irrigation_classification(samples: SampleSet, **kw) -> list[SARResult]:
    return [sar_sample(s, **kw) for s in samples]
