"""CLI do QualiGraf-Py (typer). Toda análise: saída humana (tabela) ou --json."""

from __future__ import annotations

import json as _json
from pathlib import Path

import typer

from .io import DataError, load

app = typer.Typer(add_completion=False, help="QualiGraf-Py — análise hidroquímica (FUNCEME).")
plot_app = typer.Typer(help="Diagramas: piper|stiff|durov|schoeller|radial.")
app.add_typer(plot_app, name="plot")


def _fail(msg: str, code: int = 1) -> None:
    typer.echo(f"erro: {msg}", err=True)
    raise typer.Exit(code)


def _load(file: Path):
    try:
        return load(file)
    except DataError as e:
        _fail(str(e), 2)


def _emit_rows(rows: list[dict], as_json: bool, output: Path | None) -> None:
    if as_json:
        text = _json.dumps(rows, ensure_ascii=False, indent=2)
        if output:
            output.write_text(text, encoding="utf-8")
            typer.echo(str(output))
        else:
            typer.echo(text)
        return
    if not rows:
        typer.echo("(sem resultados)")
        return
    headers = list(rows[0].keys())
    widths = {h: max(len(h), *(len(str(r.get(h, ""))) for r in rows)) for h in headers}
    line = "  ".join(h.ljust(widths[h]) for h in headers)
    typer.echo(line)
    typer.echo("  ".join("-" * widths[h] for h in headers))
    for r in rows:
        typer.echo("  ".join(str(r.get(h, "")).ljust(widths[h]) for h in headers))
    if output:
        import csv

        with output.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=headers)
            w.writeheader()
            w.writerows(rows)


# --- balance -------------------------------------------------------------------------

@app.command()
def balance(
    file: Path,
    json: bool = typer.Option(False, "--json"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """Balanço iônico e erro prático Ep% — Custódio & Llamas (1983) (US1).

    Aceitação por CE (Custódio & Llamas) e por soma de íons (Logan, 1965).
    """
    from .balance import ionic_balance

    samples = _load(file)
    results = ionic_balance(samples)
    rows = [{
        "label": r.label, "ΣCat": r.sum_cations, "ΣAn": r.sum_anions,
        "Ep%": r.ep, "tol_CE": r.tol_ce, "ok_CE": r.acceptable_ce,
        "tol_Logan": r.tol_logan, "ok_Logan": r.acceptable_logan,
        "completo": r.complete,
    } for r in results]
    _emit_rows(rows, json, output)


# --- tds -----------------------------------------------------------------------------

@app.command()
def tds(
    file: Path,
    factor: float = typer.Option(0.65, help="fator STD = CE × fator"),
    json: bool = typer.Option(False, "--json"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """STD + classificação CONAMA 357/2005 (US2)."""
    from .tds import total_dissolved_solids

    samples = _load(file)
    try:
        results = total_dissolved_solids(samples, factor=factor)
    except DataError as e:
        _fail(str(e), 3)
    rows = [{"label": r.label, "STD": r.tds, "fonte": r.source,
             "classe_CONAMA": r.conama_class} for r in results]
    _emit_rows(rows, json, output)


# --- sar -----------------------------------------------------------------------------

@app.command()
def sar(
    file: Path,
    json: bool = typer.Option(False, "--json"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """SAR + classificação USSL para irrigação (US3)."""
    from .irrigation import irrigation_classification

    samples = _load(file)
    results = irrigation_classification(samples)
    rows = [{"label": r.label, "SAR": r.sar, "C": r.c_class, "S": r.s_class,
             "USSL": r.ussl_label} for r in results]
    _emit_rows(rows, json, output)


# --- iqa -----------------------------------------------------------------------------

@app.command()
def iqa(
    file: Path,
    json: bool = typer.Option(False, "--json"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """Índice de Qualidade da Água — CETESB + IGAM (US4)."""
    from .iqa import water_quality_index

    samples = _load(file)
    typer.echo(
        "nota: curvas qi digitalizadas da Figura 01 e corroboradas pelas equações "
        "CETESB (±2–3 q). O valor de DBO exibido na tela do QualiGraf é bug do software; "
        "aqui usamos a curva correta (ver DBO_DISCREPANCY).", err=True
    )
    try:
        results = water_quality_index(samples)
    except DataError as e:
        _fail(str(e), 3)
    rows = [{"label": r.label, "IQA": r.iqa, "CETESB": r.cetesb_class,
             "IGAM": r.igam_class} for r in results]
    _emit_rows(rows, json, output)


# --- stats ---------------------------------------------------------------------------

@app.command()
def stats(
    file: Path,
    columns: str | None = typer.Option(None, help="colunas separadas por vírgula"),
    json: bool = typer.Option(False, "--json"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """Estatísticas básicas por parâmetro (US6)."""
    from .stats import basic_stats

    samples = _load(file)
    cols = [c.strip() for c in columns.split(",")] if columns else None
    result = basic_stats(samples, columns=cols)
    rows = [{"parâmetro": k, **v} for k, v in result.items()]
    _emit_rows(rows, json, output)


# --- correlate -----------------------------------------------------------------------

@app.command()
def correlate(
    file: Path,
    x: str = typer.Option(..., help="coluna X"),
    y: str = typer.Option(..., help="coluna Y"),
    model: str = typer.Option("linear", help="linear|log|exp|power"),
    json: bool = typer.Option(False, "--json"),
):
    """Correlação entre dois parâmetros + R² (US6)."""
    from .stats import correlate as _corr

    samples = _load(file)
    try:
        r = _corr(samples, x, y, model=model)
    except DataError as e:
        _fail(str(e), 3)
    _emit_rows([r.to_dict()], json, None)


# --- convert -------------------------------------------------------------------------

@app.command()
def convert(
    file: Path,
    to: str = typer.Option("meq", help="meq | mg"),
    output: Path | None = typer.Option(None, "-o", "--output"),
):
    """Converte as concentrações de íons de uma planilha entre mg/L e meq/L (US1/FR-011)."""
    from .chemistry import to_meq, to_mg
    from .constants import ANIONS, CATIONS

    samples = _load(file)
    ions = CATIONS + ANIONS
    rows = []
    for s in samples:
        row = {"label": s.label}
        for ion in ions:
            val = getattr(s, ion, None)
            if val is None:
                continue
            row[ion] = round(to_meq(val, ion) if to == "meq" else to_mg(val, ion), 4)
        rows.append(row)
    _emit_rows(rows, False, output)


# --- plot ----------------------------------------------------------------------------

def _do_plot(diagram: str, file: Path, output: Path, labels: bool, select: str | None):
    import matplotlib
    matplotlib.use("Agg")
    from .diagrams import plot as make_plot

    samples = _load(file)
    if select:
        samples = samples.select([s.strip() for s in select.split(",")])
        if len(samples) == 0:
            _fail("nenhuma amostra corresponde a --select", 3)
    try:
        kw = {"title": None}
        if diagram in ("piper", "durov", "schoeller"):
            kw["labels"] = labels
        fig = make_plot(diagram, samples, **kw)
    except (ValueError, DataError) as e:
        _fail(str(e), 3)
    fig.savefig(output, dpi=150)
    typer.echo(str(output))


@plot_app.command("piper")
def plot_piper_cmd(file: Path, output: Path = typer.Option(..., "-o", "--output"),
                   labels: bool = typer.Option(False, "--labels"),
                   select: str | None = typer.Option(None, "--select")):
    _do_plot("piper", file, output, labels, select)


@plot_app.command("stiff")
def plot_stiff_cmd(file: Path, output: Path = typer.Option(..., "-o", "--output"),
                   labels: bool = typer.Option(False, "--labels"),
                   select: str | None = typer.Option(None, "--select")):
    _do_plot("stiff", file, output, labels, select)


@plot_app.command("durov")
def plot_durov_cmd(file: Path, output: Path = typer.Option(..., "-o", "--output"),
                   labels: bool = typer.Option(False, "--labels"),
                   select: str | None = typer.Option(None, "--select")):
    _do_plot("durov", file, output, labels, select)


@plot_app.command("schoeller")
def plot_schoeller_cmd(file: Path, output: Path = typer.Option(..., "-o", "--output"),
                       labels: bool = typer.Option(False, "--labels"),
                       select: str | None = typer.Option(None, "--select")):
    _do_plot("schoeller", file, output, labels, select)


@plot_app.command("radial")
def plot_radial_cmd(file: Path, output: Path = typer.Option(..., "-o", "--output"),
                    labels: bool = typer.Option(False, "--labels"),
                    select: str | None = typer.Option(None, "--select")):
    _do_plot("radial", file, output, labels, select)


if __name__ == "__main__":
    app()
