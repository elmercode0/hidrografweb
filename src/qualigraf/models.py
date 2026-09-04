"""Modelos de dados: WaterSample, SampleSet e estruturas de resultado."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field, fields

from .constants import ANIONS, CATIONS, EQUIVALENT_WEIGHTS

# Campos numéricos de concentração/parâmetro do WaterSample.
_NUMERIC_FIELDS = (
    "ca", "mg", "na", "k", "cl", "so4", "hco3", "co3", "no3",
    "ec", "ph", "tds", "temp", "temp_var", "do_sat", "bod", "coliforms",
    "n_total", "p_total", "turbidity", "total_solids", "lat", "lon",
)


@dataclass
class WaterSample:
    """Uma amostra de água. Concentrações de íons em mg/L; CE em µS/cm."""

    label: str = ""
    ca: float | None = None
    mg: float | None = None
    na: float | None = None
    k: float | None = None
    cl: float | None = None
    so4: float | None = None
    hco3: float | None = None
    co3: float | None = None
    no3: float | None = None
    ec: float | None = None
    ph: float | None = None
    tds: float | None = None
    temp: float | None = None
    temp_var: float | None = None
    do_sat: float | None = None
    bod: float | None = None
    coliforms: float | None = None
    n_total: float | None = None
    p_total: float | None = None
    turbidity: float | None = None
    total_solids: float | None = None
    lat: float | None = None
    lon: float | None = None

    def meq(self, ion: str, weights: dict[str, float] | None = None) -> float | None:
        """Concentração do íon em meq/L (None se ausente)."""
        weights = weights or EQUIVALENT_WEIGHTS
        val = getattr(self, ion, None)
        if val is None:
            return None
        return val / weights[ion]

    def has(self, *field_names: str) -> bool:
        """True se todos os campos existem e não são None."""
        return all(getattr(self, f, None) is not None for f in field_names)

    def cations_meq(self, weights: dict[str, float] | None = None) -> dict[str, float]:
        return {i: self.meq(i, weights) or 0.0 for i in CATIONS if self.has(i)}

    def anions_meq(self, weights: dict[str, float] | None = None) -> dict[str, float]:
        return {i: self.meq(i, weights) or 0.0 for i in ANIONS if self.has(i)}


@dataclass
class SampleSet:
    """Coleção de WaterSample."""

    samples: list[WaterSample] = field(default_factory=list)

    def __iter__(self) -> Iterator[WaterSample]:
        return iter(self.samples)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> WaterSample:
        return self.samples[idx]

    def select(self, labels: list[str]) -> SampleSet:
        wanted = set(labels)
        return SampleSet([s for s in self.samples if s.label in wanted])

    def to_dataframe(self):
        import pandas as pd

        return pd.DataFrame([
            {f.name: getattr(s, f.name) for f in fields(WaterSample)} for s in self.samples
        ])


# --- Estruturas de resultado ---------------------------------------------------------

@dataclass
class BalanceResult:
    label: str
    cations_meq: dict[str, float]
    anions_meq: dict[str, float]
    sum_cations: float
    sum_anions: float
    ep: float                       # erro prático Ep% (Custódio & Llamas, 1983)
    tol_ce: float | None            # tolerância pela CE (Custódio & Llamas)
    tol_logan: float                # tolerância pela soma de íons (Logan, 1965)
    acceptable_ce: bool | None      # |Ep| ≤ tol_ce (None se não há CE)
    acceptable_logan: bool          # |Ep| ≤ tol_logan
    complete: bool = True           # todos os íons maiores presentes?
    missing_major: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "cations_meq": self.cations_meq,
            "anions_meq": self.anions_meq,
            "sum_cations": self.sum_cations,
            "sum_anions": self.sum_anions,
            "ep": self.ep,
            "tol_ce": self.tol_ce,
            "tol_logan": self.tol_logan,
            "acceptable_ce": self.acceptable_ce,
            "acceptable_logan": self.acceptable_logan,
            "complete": self.complete,
            "missing_major": list(self.missing_major),
        }


@dataclass
class TDSResult:
    label: str
    tds: float
    source: str  # "measured" | "estimated"
    ec: float | None
    factor: float
    conama_class: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class SARResult:
    label: str
    sar: float | None
    ec: float | None
    c_class: str | None
    s_class: str | None
    ussl_label: str | None

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class IQAResult:
    label: str
    iqa: float
    qi: dict[str, float]
    cetesb_class: str
    igam_class: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class CorrelationResult:
    x: str
    y: str
    model: str
    coeffs: list[float]
    r2: float
    n: int

    def to_dict(self) -> dict:
        return self.__dict__.copy()
