"""US6 — Estatísticas básicas e correlação entre íons (T026)."""

from __future__ import annotations

import numpy as np

from .io import DataError
from .models import CorrelationResult, SampleSet


def basic_stats(samples: SampleSet, columns: list[str] | None = None) -> dict[str, dict]:
    """n, min, max, média, variância (amostral) e desvio-padrão por coluna numérica."""
    df = samples.to_dataframe()
    num = df.select_dtypes(include="number")
    if columns:
        keep = [c for c in columns if c in num.columns]
        num = num[keep]

    out: dict[str, dict] = {}
    for col in num.columns:
        series = num[col].dropna()
        if len(series) == 0:
            continue
        arr = series.to_numpy(dtype=float)
        out[col] = {
            "n": int(arr.size),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "variance": float(np.var(arr, ddof=1)) if arr.size > 1 else 0.0,
            "std": float(np.std(arr, ddof=1)) if arr.size > 1 else 0.0,
        }
    return out


def _transform(x, y, model):
    """Retorna (X, Y, fit->coeffs, predict) para o modelo escolhido."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if model == "linear":
        return x, y
    if model == "log":  # y = a + b*ln(x)
        return np.log(x), y
    if model == "exp":  # y = a*e^(b x) -> ln y = ln a + b x
        return x, np.log(y)
    if model == "power":  # y = a*x^b -> ln y = ln a + b ln x
        return np.log(x), np.log(y)
    raise DataError(f"modelo desconhecido: {model}")


def correlate(
    samples: SampleSet, x_col: str, y_col: str, model: str = "linear"
) -> CorrelationResult:
    """Ajuste por mínimos quadrados + R². Modelos: linear|log|exp|power."""
    df = samples.to_dataframe()
    for c in (x_col, y_col):
        if c not in df.columns:
            raise DataError(f"correlação requer coluna '{c}' (ausente)")
    pair = df[[x_col, y_col]].dropna()
    if len(pair) < 2:
        raise DataError("correlação requer ao menos 2 pares válidos")

    x = pair[x_col].to_numpy(dtype=float)
    y = pair[y_col].to_numpy(dtype=float)

    # Guardas de positividade: log(x) e ln(y) exigem valores > 0.
    if model in ("log", "power") and np.any(x <= 0):
        raise DataError(f"modelo '{model}' exige {x_col} > 0 (há valores ≤ 0)")
    if model in ("exp", "power") and np.any(y <= 0):
        raise DataError(f"modelo '{model}' exige {y_col} > 0 (há valores ≤ 0)")

    X, Y = _transform(x, y, model)

    b, a = np.polyfit(X, Y, 1)  # slope, intercept
    y_pred = a + b * X
    ss_res = float(np.sum((Y - y_pred) ** 2))
    ss_tot = float(np.sum((Y - np.mean(Y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return CorrelationResult(
        x=x_col, y=y_col, model=model,
        coeffs=[round(float(a), 6), round(float(b), 6)],  # [intercept, slope] no espaço transformado
        r2=round(r2, 6),
        n=len(pair),
    )
