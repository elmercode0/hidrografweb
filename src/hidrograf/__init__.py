"""Hidrograf — núcleo de análise hidroquímica (reimplementação do QualiGraf/FUNCEME)."""

from .balance import ionic_balance
from .io import load
from .iqa import water_quality_index
from .irrigation import irrigation_classification
from .stats import basic_stats, correlate
from .tds import total_dissolved_solids

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "basic_stats",
    "correlate",
    "ionic_balance",
    "irrigation_classification",
    "load",
    "total_dissolved_solids",
    "water_quality_index",
]
