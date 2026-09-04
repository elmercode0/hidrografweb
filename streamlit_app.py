"""QualiGraf-Py — UI web (Streamlit).

Camada de interface fina sobre a biblioteca `qualigraf` (cálculos puros). Faz upload de
uma planilha de amostras e mostra tabelas + diagramas hidroquímicos.

Deploy: Streamlit Community Cloud (share.streamlit.io) → aponte para este arquivo.
Local:  `streamlit run streamlit_app.py`
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Permite importar `qualigraf` do src/ sem instalar o pacote (funciona no cloud e local).
sys.path.insert(0, str(Path(__file__).parent / "src"))
os.environ.setdefault("MPLBACKEND", "Agg")

import pandas as pd
import streamlit as st

from qualigraf.balance import ionic_balance
from qualigraf.diagrams import plot as make_plot
from qualigraf.io import DataError, load
from qualigraf.iqa import water_quality_index
from qualigraf.irrigation import irrigation_classification
from qualigraf.models import SampleSet, WaterSample
from qualigraf.stats import basic_stats, correlate
from qualigraf.tds import total_dissolved_solids

EXAMPLE = Path(__file__).parent / "tests" / "data" / "sample_waters.csv"

st.set_page_config(page_title="QualiGraf-Py", page_icon="💧", layout="wide")


@st.cache_data(show_spinner=False)
def _load_bytes(data: bytes, name: str) -> list[dict]:
    """Carrega bytes de upload em uma lista de dicts (cacheável)."""
    suffix = Path(name).suffix or ".csv"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as fh:
        fh.write(data)
        tmp = fh.name
    try:
        ss = load(tmp)
        return [s.__dict__ for s in ss]
    finally:
        os.unlink(tmp)


def _to_sampleset(records: list[dict]) -> SampleSet:
    return SampleSet([WaterSample(**r) for r in records])


def _df(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------- Sidebar
st.sidebar.title("💧 QualiGraf-Py")
st.sidebar.caption(
    "Análise hidroquímica — reimplementação em Python dos módulos do QualiGraf (FUNCEME)."
)

up = st.sidebar.file_uploader("Planilha de amostras (CSV/XLSX)", type=["csv", "xlsx"])
use_example = st.sidebar.toggle("Usar dados de exemplo", value=up is None)

samples: SampleSet | None = None
try:
    if up is not None and not use_example:
        recs = _load_bytes(up.getvalue(), up.name)
        samples = _to_sampleset(recs)
    elif use_example:
        samples = load(EXAMPLE)
except DataError as e:
    st.sidebar.error(f"Erro ao ler a planilha: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Unidades:** íons em mg/L · CE em µS/cm.\n\n"
    "Colunas reconhecidas por apelido (ex.: `Na`, `Sodio`, `Na+`)."
)

# ------------------------------------------------------------------------------- Main
st.title("QualiGraf-Py")
if samples is None:
    st.info("Envie uma planilha na barra lateral ou ative **Usar dados de exemplo**.")
    st.stop()

st.success(f"{len(samples)} amostra(s) carregada(s).")

tabs = st.tabs(
    ["📊 Dados", "⚖️ Balanço iônico", "🧂 STD/CONAMA", "🌱 Irrigação SAR/USSL",
     "🏅 IQA", "📈 Estatísticas", "🔗 Correlação", "📐 Diagramas"]
)

# --- Dados
with tabs[0]:
    st.subheader("Amostras")
    st.dataframe(samples.to_dataframe(), use_container_width=True)

# --- Balanço iônico
with tabs[1]:
    st.subheader("Balanço iônico — erro prático Ep% (Custódio & Llamas, 1983)")
    rows = [{
        "label": r.label, "ΣCát": r.sum_cations, "ΣÂn": r.sum_anions, "Ep%": r.ep,
        "tol_CE": r.tol_ce, "ok_CE": r.acceptable_ce,
        "tol_Logan": r.tol_logan, "ok_Logan": r.acceptable_logan, "completo": r.complete,
    } for r in ionic_balance(samples)]
    st.dataframe(_df(rows), use_container_width=True)
    st.caption(
        "Aceitação por CE (Custódio & Llamas) e por soma de íons (Logan, 1965). "
        "Ep% = 100·(Σân−Σcát)/(½·(Σcát+Σân))."
    )

# --- STD / CONAMA
with tabs[2]:
    st.subheader("Sólidos Totais Dissolvidos + classificação CONAMA 357/2005")
    factor = st.slider("Fator STD = CE × fator", 0.55, 0.75, 0.65, 0.01)
    try:
        rows = [{"label": r.label, "STD (mg/L)": r.tds, "fonte": r.source,
                 "classe": r.conama_class} for r in total_dissolved_solids(samples, factor=factor)]
        st.dataframe(_df(rows), use_container_width=True)
    except DataError as e:
        st.error(str(e))

# --- SAR / USSL
with tabs[3]:
    st.subheader("Classificação para irrigação — SAR + USSL (Richards, 1954)")
    rows = [{"label": r.label, "SAR": r.sar, "C (salinidade)": r.c_class,
             "S (sódio)": r.s_class, "USSL": r.ussl_label}
            for r in irrigation_classification(samples)]
    st.dataframe(_df(rows), use_container_width=True)

# --- IQA
with tabs[4]:
    st.subheader("Índice de Qualidade da Água — CETESB + IGAM")
    st.info(
        "Curvas qi digitalizadas da Figura 01 do QualiGraf e corroboradas pelas equações "
        "CETESB (±2–3 q). Trate como estimativa. Requer os 9 parâmetros do IQA.",
        icon="ℹ️",
    )
    try:
        rows = [{"label": r.label, "IQA": r.iqa, "CETESB": r.cetesb_class, "IGAM": r.igam_class}
                for r in water_quality_index(samples)]
        st.dataframe(_df(rows), use_container_width=True)
    except DataError as e:
        st.warning(f"IQA indisponível: {e}")

# --- Estatísticas
with tabs[5]:
    st.subheader("Estatísticas básicas por parâmetro")
    stats = basic_stats(samples)
    rows = [{"parâmetro": k, **v} for k, v in stats.items()]
    st.dataframe(_df(rows), use_container_width=True)

# --- Correlação
with tabs[6]:
    st.subheader("Correlação entre parâmetros (mínimos quadrados + R²)")
    num_cols = list(samples.to_dataframe().select_dtypes(include="number").columns)
    if len(num_cols) < 2:
        st.warning("São necessárias ao menos 2 colunas numéricas.")
    else:
        c1, c2, c3 = st.columns(3)
        x = c1.selectbox("X", num_cols, index=num_cols.index("cl") if "cl" in num_cols else 0)
        y = c2.selectbox("Y", num_cols, index=num_cols.index("na") if "na" in num_cols else 1)
        model = c3.selectbox("Modelo", ["linear", "log", "exp", "power"])
        try:
            r = correlate(samples, x, y, model=model)
            m1, m2, m3 = st.columns(3)
            m1.metric("R²", f"{r.r2:.4f}")
            m2.metric("Coef. (intercepto, incl.)", f"{r.coeffs}")
            m3.metric("n", r.n)
        except DataError as e:
            st.error(str(e))

# --- Diagramas
with tabs[7]:
    st.subheader("Diagramas hidroquímicos")
    c1, c2 = st.columns([1, 3])
    kind = c1.selectbox("Tipo", ["piper", "stiff", "durov", "schoeller", "radial"])
    labels = c1.checkbox("Rótulos", value=True)
    try:
        fig = make_plot(kind, samples, labels=labels, title=None)
        c2.pyplot(fig, use_container_width=True)
    except (ValueError, DataError) as e:
        c2.error(str(e))
    c1.caption("Stiff mostra até 6 amostras; Radial usa a primeira amostra.")
