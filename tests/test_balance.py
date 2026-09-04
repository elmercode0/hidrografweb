from hidrograf.balance import (
    balance_sample,
    practical_error,
    tolerance_ce,
    tolerance_sum,
)
from hidrograf.models import WaterSample


def test_ep_custodio_llamas_formula():
    # Custódio & Llamas: Ep = 100*(Σan - Σcat)/(0.5*(Σcat+Σan)).
    # Σcat=4, Σan=3  ->  100*(-1)/(0.5*7) = -28.571%
    assert abs(practical_error(4.0, 3.0) - (-28.571)) < 0.01


def test_ep_zero_when_balanced():
    # Ca=40.08(2 meq)+Mg=24.30(2 meq)=4 cátions; Cl=35.45(1)+HCO3=183.06(3)=4 ânions
    s = WaterSample(label="X", ca=40.08, mg=24.30, cl=35.45, hco3=183.06)
    r = balance_sample(s)
    assert abs(r.sum_cations - 4.0) < 1e-3
    assert abs(r.sum_anions - 4.0) < 1e-3
    assert abs(r.ep) < 0.05
    assert r.acceptable_logan is True


def test_tolerance_tables():
    # Custódio & Llamas (CE): 500->8%, interpola 600->~7.73%
    assert tolerance_ce(500) == 8.0
    assert 7.5 < tolerance_ce(600) < 8.0
    assert tolerance_ce(50) == 30.0
    assert tolerance_ce(5000) == 4.0
    # Logan (soma meq/L): <1->15, 1-2->10, 2-6->6, 6-10->4
    assert tolerance_sum(0.5) == 15.0
    assert tolerance_sum(1.5) == 10.0
    assert tolerance_sum(4.0) == 6.0
    assert tolerance_sum(20.0) == 4.0


def test_acceptance_both_criteria():
    # Σcat≈4.15, Σan≈3.72, Ep≈-10.9%, CE=600 -> tol_CE≈7.7 (reprova), Logan 6% (reprova)
    s = WaterSample(label="P1", ca=40, mg=12, na=25, k=3, cl=30, so4=20, hco3=150, ec=600)
    r = balance_sample(s)
    assert r.tol_ce is not None
    assert r.acceptable_ce is False
    assert r.acceptable_logan is False


def test_acceptable_ce_none_without_ec():
    s = WaterSample(label="Q", ca=40.08, mg=24.30, cl=35.45, hco3=183.06)
    r = balance_sample(s)
    assert r.tol_ce is None
    assert r.acceptable_ce is None


def test_complete_flag():
    full = WaterSample(label="F", ca=40.08, mg=24.30, na=23, cl=35.45, so4=48, hco3=61)
    assert balance_sample(full).complete is True
    partial = WaterSample(label="P", ca=40.08, cl=35.45)
    r = balance_sample(partial)
    assert r.complete is False
    assert "mg" in r.missing_major
