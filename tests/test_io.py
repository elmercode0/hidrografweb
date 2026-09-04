import pytest

from qualigraf.io import DataError, detect_ion_units, load


def test_load_ok():
    s = load("tests/data/sample_waters.csv")
    assert len(s) == 4
    assert s[0].label == "P1"


def test_invalid_value_reported(tmp_path):
    p = tmp_path / "bad.csv"
    p.write_text("label,Ca,Cl\nP1,40,30\nP2,abc,20\n", encoding="utf-8")
    with pytest.raises(DataError) as e:
        load(p)
    # deve citar a amostra e o valor inválido, não descartar em silêncio
    assert "P2" in str(e.value)
    assert "abc" in str(e.value)


def test_empty_cell_is_missing_not_invalid(tmp_path):
    p = tmp_path / "gap.csv"
    p.write_text("label,Ca,Cl\nP1,40,\n", encoding="utf-8")
    s = load(p)  # célula vazia = ausente (None), não erro
    assert s[0].cl is None
    assert s[0].ca == 40.0


def test_missing_file():
    with pytest.raises(DataError):
        load("nao_existe.csv")


def test_default_unit_meq_converts_to_mg(tmp_path):
    # Ca=2 meq/L deve virar 2*20.04 = 40.08 mg/L internamente.
    p = tmp_path / "meq.csv"
    p.write_text("label,Ca,Na\nP1,2,1\n", encoding="utf-8")
    s = load(p, default_unit="meq")
    assert abs(s[0].ca - 40.08) < 1e-6
    assert abs(s[0].na - 22.99) < 1e-6
    # e o meq() volta ao valor de entrada
    assert abs(s[0].meq("ca") - 2.0) < 1e-6


def test_header_unit_overrides_default(tmp_path):
    # Cabeçalho diz meq p/ Na; Ca sem unidade usa default mg.
    p = tmp_path / "mix.csv"
    p.write_text("label,Ca,Na (meq/L)\nP1,40.08,1\n", encoding="utf-8")
    s = load(p, default_unit="mg")
    assert abs(s[0].ca - 40.08) < 1e-6          # mg (default)
    assert abs(s[0].na - 22.99) < 1e-6          # meq->mg (cabeçalho)


def test_mg_ion_symbol_not_confused_with_milligram(tmp_path):
    # Coluna "Mg" (magnésio) sem unidade não deve ser lida como miligrama.
    p = tmp_path / "mg.csv"
    p.write_text("label,Mg\nP1,12.15\n", encoding="utf-8")
    assert detect_ion_units(p) == {"mg": None}
    s = load(p, default_unit="meq")
    assert abs(s[0].mg - 12.15 * 12.15) < 1e-3   # tratado como meq (default), convertido


def test_detect_ion_units(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("label,Na (meq/L),Cl_mg/L,Ca\nP1,1,2,3\n", encoding="utf-8")
    u = detect_ion_units(p)
    assert u["na"] == "meq"
    assert u["cl"] == "mg"
    assert u["ca"] is None
