from hidrograf.models import SampleSet, WaterSample
from hidrograf.stats import basic_stats, correlate


def _set():
    return SampleSet([
        WaterSample(label="A", cl=10, na=20),
        WaterSample(label="B", cl=20, na=40),
        WaterSample(label="C", cl=30, na=60),
    ])


def test_basic_stats_mean_std():
    st = basic_stats(_set(), columns=["cl"])
    assert st["cl"]["n"] == 3
    assert st["cl"]["mean"] == 20.0
    assert st["cl"]["min"] == 10.0
    assert st["cl"]["max"] == 30.0
    # variância amostral de [10,20,30] = 100
    assert abs(st["cl"]["variance"] - 100.0) < 1e-9


def test_correlation_perfect_linear():
    r = correlate(_set(), "cl", "na", model="linear")
    assert abs(r.r2 - 1.0) < 1e-9  # na = 2*cl exatamente
    assert abs(r.coeffs[1] - 2.0) < 1e-6  # slope = 2
    assert r.n == 3


def test_correlation_log_requires_positive():
    import pytest

    from hidrograf.io import DataError
    from hidrograf.models import SampleSet, WaterSample

    ss = SampleSet([
        WaterSample(label="A", cl=0, na=10),  # cl=0 inválido para log
        WaterSample(label="B", cl=10, na=20),
    ])
    with pytest.raises(DataError):
        correlate(ss, "cl", "na", model="log")
