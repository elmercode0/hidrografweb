import pytest

from hidrograf.io import DataError
from hidrograf.iqa import iqa_sample
from hidrograf.iqa_curves import ANCHOR_POINTS, DBO_DISCREPANCY, qi
from hidrograf.models import WaterSample

_FULL = {
    "do_sat": 90, "coliforms": 50, "ph": 7.0, "bod": 2, "temp_var": 1,
    "n_total": 1.0, "p_total": 0.05, "turbidity": 5, "total_solids": 350,
}


def test_qi_matches_hidrograf_anchor_points():
    """8 dos 9 pontos-âncora do exemplo do QualiGraf conferem com as curvas digitalizadas.

    DBO é a exceção documentada (DBO_DISCREPANCY): a curva desenhada dá ~22 em DBO=15,
    mas o exemplo do software mostra 67,57. Aqui validamos as 8 curvas coerentes.
    """
    tol = 3.0  # erro típico de leitura gráfica
    for param, (observed, qi_ref) in ANCHOR_POINTS.items():
        if param == DBO_DISCREPANCY["param"]:
            continue  # divergência conhecida
        assert abs(qi(param, observed) - qi_ref) <= tol, (
            f"{param}: qi({observed})={qi(param, observed):.1f} vs ref {qi_ref}"
        )


def test_dbo_discrepancy_is_documented():
    # A curva desenhada (usada) diverge do exemplo do software — registrado, não escondido.
    assert abs(qi("bod", 15.0) - DBO_DISCREPANCY["qi_curva_desenhada"]) <= 4
    assert DBO_DISCREPANCY["qi_exemplo_hidrograf"] == 67.57


def test_iqa_good_water_high_index():
    r = iqa_sample(WaterSample(label="G", **_FULL))
    assert 0 <= r.iqa <= 100
    assert r.iqa > 60
    assert r.cetesb_class in ("Bom", "Ótimo")


def test_iqa_missing_param_raises():
    partial = dict(_FULL)
    del partial["do_sat"]
    with pytest.raises(DataError) as e:
        iqa_sample(WaterSample(label="M", **partial))
    assert "do_sat" in str(e.value)


def test_iqa_poor_water_low_index():
    poor = {"do_sat": 30, "coliforms": 100000, "ph": 5, "bod": 30, "temp_var": 8,
            "n_total": 20, "p_total": 5, "turbidity": 200, "total_solids": 5000}
    r = iqa_sample(WaterSample(label="B", **poor))
    assert r.iqa < 40
    assert r.cetesb_class in ("Ruim", "Péssima", "Aceitável")


def test_iqa_classes_exact_boundaries():
    # Faixas exatas do QualiGraf: CETESB 20/37/52/80; IGAM 25/50/70/90.
    from hidrograf.constants import IQA_RANGES_CETESB, IQA_RANGES_IGAM
    from hidrograf.iqa import _classify

    assert _classify(80, IQA_RANGES_CETESB) == "Ótimo"
    assert _classify(52, IQA_RANGES_CETESB) == "Bom"
    assert _classify(19.9, IQA_RANGES_CETESB) == "Péssima"
    assert _classify(25, IQA_RANGES_IGAM) == "Muito Ruim"
    assert _classify(90, IQA_RANGES_IGAM) == "Bom"
    assert _classify(90.5, IQA_RANGES_IGAM) == "Excelente"
