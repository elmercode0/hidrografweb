import matplotlib

matplotlib.use("Agg")

import pytest

from qualigraf.diagrams import plot
from qualigraf.io import load

_CSV = "tests/data/sample_waters.csv"


@pytest.mark.parametrize("kind", ["piper", "stiff", "durov", "schoeller", "radial"])
def test_plot_creates_nonempty_file(kind, tmp_path):
    samples = load(_CSV)
    out = tmp_path / f"{kind}.png"
    fig = plot(kind, samples, labels=True)
    fig.savefig(out, dpi=100)
    assert out.exists() and out.stat().st_size > 0
