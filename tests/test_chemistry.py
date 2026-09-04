from hidrograf.chemistry import to_meq, to_mg


def test_calcium_mg_to_meq():
    # 40.08 mg/L de Ca / 20.04 = 2.0 meq/L
    assert to_meq(40.08, "ca") == 2.0


def test_roundtrip():
    assert abs(to_mg(to_meq(100.0, "na"), "na") - 100.0) < 1e-9


def test_unknown_ion():
    import pytest

    with pytest.raises(KeyError):
        to_meq(1.0, "xx")


def test_do_saturation():
    from hidrograf.chemistry import do_saturation_mgl, do_saturation_pct

    # Saturação ~9.08 mg/L a 20 °C ao nível do mar (APHA).
    assert abs(do_saturation_mgl(20.0) - 9.08) < 0.15
    # OD medido = saturação -> 100%
    cs = do_saturation_mgl(25.0)
    assert abs(do_saturation_pct(cs, 25.0) - 100.0) < 0.01
    # Altitude reduz a saturação
    assert do_saturation_mgl(20.0, altitude_m=1000) < do_saturation_mgl(20.0)
