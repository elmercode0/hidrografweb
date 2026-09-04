"""Carregamento de amostras de CSV/XLSX com mapeamento de aliases e de unidades (T007).

As concentrações de íons podem vir em **mg/L** ou **meq/L**. A unidade é detectada pelo
cabeçalho de cada coluna (ex.: `Na (meq/L)`, `Cl_mg/L`, `SO4 (epm)`); onde o cabeçalho não
indica, usa-se `default_unit`. Internamente tudo é normalizado para **mg/L** (os cálculos
convertem para meq/L quando necessário).
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from .constants import ANIONS, CATIONS, COLUMN_ALIASES, EQUIVALENT_WEIGHTS
from .models import SampleSet, WaterSample

_VALID_FIELDS = set(WaterSample().__dict__.keys())
_ION_FIELDS = set(CATIONS) | set(ANIONS)


class DataError(Exception):
    """Erro de dados de entrada (arquivo/colunas)."""


def _normalize(col: str) -> str:
    return str(col).strip().lower().replace(" ", "_")


def _unit_token(text: str) -> str | None:
    """Interpreta um trecho de unidade: 'meq'/'epm' → meq; 'mg/l'/'(mg)' → mg; senão None."""
    h = str(text).strip().lower()
    if "meq" in h or "epm" in h:
        return "meq"
    if re.search(r"mg\s*/\s*l|\(\s*mg\s*\)|mg\s*l\b|^mg$", h):
        return "mg"
    return None


def _split_header(header: str) -> tuple[str, str | None]:
    """Separa o nome do íon da unidade no cabeçalho.

    'Na (meq/L)' → ('Na', 'meq'); 'Cl_mg/L' → ('Cl', 'mg'); 'Mg' → ('Mg', None).
    O símbolo 'Mg' (magnésio) sozinho NÃO é lido como miligrama (unidade exige separador
    ou parênteses).
    """
    h = str(header).strip()
    unit = None
    # (a) unidade entre parênteses
    m = re.search(r"\(([^)]*)\)", h)
    if m:
        unit = _unit_token(m.group(1))
        h = re.sub(r"\([^)]*\)", "", h).strip()
    # (b) sufixo após separador: Cl_mg/L, Na meq/L, SO4 meq
    if unit is None:
        m2 = re.search(r"[_\s/]+((?:meq|epm|mg)\s*/?\s*l?)\s*$", h, flags=re.IGNORECASE)
        if m2:
            u = _unit_token(m2.group(1))
            if u:
                unit = u
                h = h[: m2.start()].strip()
    return h, unit


def _detect_unit(header: str) -> str | None:
    """Unidade detectada no cabeçalho (só a parte de unidade)."""
    return _split_header(header)[1]


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


def _read_df(path: str | Path):
    import pandas as pd

    p = Path(path)
    if not p.exists():
        raise DataError(f"arquivo não encontrado: {p}")
    suffix = p.suffix.lower()
    if suffix in (".csv", ".txt"):
        return pd.read_csv(p)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(p)
    raise DataError(f"formato não suportado: {suffix} (use .csv ou .xlsx)")


def _parse_columns(df) -> dict[str, tuple[str, str | None]]:
    """Coluna original -> (campo do modelo, unidade detectada|None)."""
    out: dict[str, tuple[str, str | None]] = {}
    for col in df.columns:
        base, unit = _split_header(col)
        field = COLUMN_ALIASES.get(_normalize(base))
        if field:
            out[col] = (field, unit)
    return out


def detect_ion_units(path: str | Path) -> dict[str, str | None]:
    """Para cada íon presente na planilha, a unidade detectada no cabeçalho (ou None).

    Ex.: {'na': 'meq', 'ca': None, 'cl': 'mg'}. Útil para a UI decidir se pergunta a
    unidade ao usuário (quando há None).
    """
    df = _read_df(path)
    return {
        field: unit
        for _, (field, unit) in _parse_columns(df).items()
        if field in _ION_FIELDS
    }


def load(path: str | Path, default_unit: str = "mg") -> SampleSet:
    """Carrega um CSV/XLSX em SampleSet, normalizando íons para mg/L.

    default_unit ∈ {'mg', 'meq'}: unidade assumida para colunas de íons cujo cabeçalho
    não indica a unidade. Colunas com unidade no cabeçalho têm precedência.
    """
    if default_unit not in ("mg", "meq"):
        raise DataError(f"default_unit inválido: {default_unit!r} (use 'mg' ou 'meq')")

    df = _read_df(path)
    parsed = _parse_columns(df)  # col -> (field, unit|None)

    samples: list[WaterSample] = []
    for idx, row in df.iterrows():
        kwargs: dict = {}
        label = None
        invalid: list[str] = []
        for col, (field, unit) in parsed.items():
            if field == "label":
                label = str(row[col]) if row[col] is not None else ""
                continue
            coerced = _coerce(row[col])
            if coerced is _INVALID:
                invalid.append(f"{col}={row[col]!r}")
                coerced = None
            # Normaliza íons em meq/L -> mg/L (mg = meq × peso equivalente).
            eff_unit = unit or default_unit
            if coerced is not None and field in _ION_FIELDS and eff_unit == "meq":
                coerced = coerced * EQUIVALENT_WEIGHTS[field]
            kwargs[field] = coerced
        kwargs["label"] = label or f"S{idx + 1}"
        if invalid:
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
