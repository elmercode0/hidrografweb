import pytest

from hidrograf.io import DataError
from hidrograf.models import WaterSample
from hidrograf.tds import classify_tds, tds_sample


def test_estimate_from_ec():
    s = WaterSample(label="A", ec=1000)
    r = tds_sample(s, factor=0.65)
    assert r.tds == 650.0
    assert r.source == "estimated"
    assert r.conama_class == "Salobra"  # 500 < 650 ≤ 1500


def test_measured_takes_precedence():
    s = WaterSample(label="B", ec=1000, tds=300)
    r = tds_sample(s)
    assert r.tds == 300.0
    assert r.source == "measured"
    assert r.conama_class == "Doce"


def test_classes():
    # Faixas do QualiGraf (Tutorial pág. 12): Doce 0–500, Salobra 500–1500,
    # Salgada 1500–35000, Salmoura >35000.
    assert classify_tds(400) == "Doce"
    assert classify_tds(1000) == "Salobra"
    assert classify_tds(2730) == "Salgada"   # antes era erroneamente "Salobra"
    assert classify_tds(5000) == "Salgada"
    assert classify_tds(40000) == "Salmoura"


def test_requires_ec_or_tds():
    with pytest.raises(DataError):
        tds_sample(WaterSample(label="C"))
