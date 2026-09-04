"""Carregamento de amostras de CSV/XLSX com mapeamento de aliases (T007)."""

from __future__ import annotations

import math
from pathlib import Path

from .constants import COLUMN_ALIASES
from .models import SampleSet, WaterSample

_VALID_FIELDS = set(WaterSample().__dict__.keys())


class DataError(Exception):
    """Erro de dados de entrada (arquivo/colunas)."""


def _normalize(col: str) -> str:
    return str(col).strip().lower().replace(" ", "_")


_INVALID = object()  # sentinela: valor presente mas não numérico


def _coerce(value):
    """Retorna float, None (vazio/ausente) ou _INVALID (presente mas não numérico)."""
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip().replace(",", ".")
        if value == "":
            return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return _INVALID
    if math.isnan(f):
        return None
    return f


def load(path: str | Path) -> SampleSet:
    """Carrega um CSV ou XLSX em um SampleSet, mapeando colunas por alias."""
    import pandas as pd

    p = Path(path)
    if not p.exists():
        raise DataError(f"arquivo não encontrado: {p}")

    suffix = p.suffix.lower()
    if suffix in (".csv", ".txt"):
        df = pd.read_csv(p)
    elif suffix in (".xlsx", ".xls"):
        df = pd.read_excel(p)
    else:
        raise DataError(f"formato não suportado: {suffix} (use .csv ou .xlsx)")

    # Mapeia colunas -> campos do modelo.
    mapping: dict[str, str] = {}
    for col in df.columns:
        field = COLUMN_ALIASES.get(_normalize(col))
        if field:
            mapping[col] = field

    samples: list[WaterSample] = []
    invalid: list[str] = []
    for idx, row in df.iterrows():
        kwargs: dict = {}
        label = None
        for col, field in mapping.items():
            if field == "label":
                label = str(row[col]) if row[col] is not None else ""
            else:
                coerced = _coerce(row[col])
                if coerced is _INVALID:
                    invalid.append(f"{col}={row[col]!r}")
                    coerced = None
                kwargs[field] = coerced
        kwargs["label"] = label or f"S{idx + 1}"
        if invalid:
            # reporta imediatamente citando a amostra (Princípio V: não descartar em silêncio)
            raise DataError(
                f"valor(es) não numérico(s) na amostra {kwargs['label']}: "
                + ", ".join(invalid)
            )
        samples.append(WaterSample(**kwargs))

    if not samples:
        raise DataError("nenhuma amostra encontrada no arquivo")
    return SampleSet(samples)


def require_columns(samples: SampleSet, analysis: str, *columns: str) -> None:
    """Valida que TODAS as amostras têm as colunas exigidas por uma análise."""
    for s in samples:
        for c in columns:
            if getattr(s, c, None) is None:
                raise DataError(
                    f"análise '{analysis}' requer '{c}' (ausente na amostra {s.label})"
                )
