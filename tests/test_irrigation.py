from qualigraf.irrigation import sar_sample, sar_value
from qualigraf.models import WaterSample


def test_sar_hand_computed():
    # Na=10, Ca=8, Mg=0 meq -> SAR = 10 / sqrt((8+0)/2) = 10/2 = 5
    assert abs(sar_value(10, 8, 0) - 5.0) < 1e-9


def test_sar_undefined_when_no_cations():
    assert sar_value(10, 0, 0) is None


def test_ussl_label():
    # Na=460 mg/L (~20 meq), Ca=40.08 (2), Mg=0 -> SAR = 20/1 = 20 -> S3
    # EC=1000 -> C3
    s = WaterSample(label="P", na=459.8, ca=40.08, mg=0.0, ec=1000)
    r = sar_sample(s)
    assert r.s_class == "S3"
    assert r.c_class == "C3"
    assert r.ussl_label == "C3S3"


def test_sar_none_without_na():
    s = WaterSample(label="Q", ca=40.08, ec=300)
    r = sar_sample(s)
    assert r.sar is None
    assert r.ussl_label is None
