import pytest

from qualigraf.io import DataError, load


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
