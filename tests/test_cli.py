import json

from typer.testing import CliRunner

from qualigraf.cli import app

runner = CliRunner()
_CSV = "tests/data/sample_waters.csv"


def test_balance_human():
    res = runner.invoke(app, ["balance", _CSV])
    assert res.exit_code == 0
    assert "Ep%" in res.stdout
    assert "ok_Logan" in res.stdout


def test_tds_json():
    res = runner.invoke(app, ["tds", _CSV, "--json"])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert data[0]["classe_CONAMA"] in ("Doce", "Salobra", "Salgada")


def test_sar_json():
    res = runner.invoke(app, ["sar", _CSV, "--json"])
    assert res.exit_code == 0
    assert "USSL" in res.stdout


def test_iqa_ok():
    res = runner.invoke(app, ["iqa", _CSV, "--json"])
    assert res.exit_code == 0
    data = json.loads(res.stdout)
    assert 0 <= data[0]["IQA"] <= 100


def test_missing_file_errors():
    res = runner.invoke(app, ["balance", "nao_existe.csv"])
    assert res.exit_code != 0


def test_plot_piper(tmp_path):
    out = tmp_path / "piper.png"
    res = runner.invoke(app, ["plot", "piper", _CSV, "-o", str(out)])
    assert res.exit_code == 0
    assert out.exists() and out.stat().st_size > 0
