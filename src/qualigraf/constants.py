"""Constantes científicas do QualiGraf-Py.

Todas as constantes citam sua fonte. Valores são overridáveis pelos módulos de
cálculo (parâmetros de função), conforme o QualiGraf original permite alterar os
fatores de conversão. Ver specs/001-qualigraf-core/research.md.
"""

from __future__ import annotations

# --- Pesos equivalentes (mg por meq) -------------------------------------------------
# peso_equivalente = massa_molar / valência. meq/L = (mg/L) / peso_equivalente.
# Fonte: massas atômicas padrão IUPAC.
EQUIVALENT_WEIGHTS: dict[str, float] = {
    "ca": 20.04,   # Ca2+
    "mg": 12.15,   # Mg2+
    "na": 22.99,   # Na+
    "k": 39.10,    # K+
    "cl": 35.45,   # Cl-
    "so4": 48.03,  # SO4 2-
    "hco3": 61.02, # HCO3-
    "co3": 30.00,  # CO3 2-
    "no3": 62.00,  # NO3-
}

CATIONS = ("ca", "mg", "na", "k")
ANIONS = ("cl", "so4", "hco3", "co3", "no3")

# --- Balanço iônico — erro prático Ep% (Custódio & Llamas, 1983) ----------------------
# Ep(%) = 100 · (Σânions − Σcátions) / [½ · (Σcátions + Σânions)]   (meq/L)
# As "duas técnicas" do QualiGraf são a MESMA fórmula com DUAS tabelas de tolerância:
#   (a) por CE — Custódio & Llamas (1983);  (b) por soma de íons — Logan (1965).
# Fontes: ABQ/CBQ 2009 (4-59-15) e Custódio & Llamas, Hidrología Subterránea (1983).

# Tolerância pela Condutividade Elétrica — (CE µS/cm, erro máx %). Interpolado.
BALANCE_TOLERANCE_CE: tuple[tuple[float, float], ...] = (
    (50.0, 30.0),
    (200.0, 10.0),
    (500.0, 8.0),
    (2000.0, 4.0),
)  # CE > 2000 → 4% (limite inferior)

# Tolerância pela soma de ânions/cátions (Logan, 1965) — (limite_sup meq/L, erro máx %).
BALANCE_TOLERANCE_SUM: tuple[tuple[float, float], ...] = (
    (1.0, 15.0),
    (2.0, 10.0),
    (6.0, 6.0),
    (10.0, 4.0),
)  # soma > 10 → 4%

# --- STD (Sólidos Totais Dissolvidos) ------------------------------------------------
# STD (mg/L) = CE (µS/cm) × fator. Fator ∈ [0.55, 0.75]; QualiGraf usa 0.65.
TDS_FACTOR: float = 0.65

# Classificação por STD (mg/L) conforme a tabela do QualiGraf (Tutorial, pág. 12),
# atribuída à Resolução CONAMA 357/2005. (nome_classe, limite_superior_inclusive).
# Fonte primária: scrapling/assets/Tutorial_QualiGraf.pdf, seção 4.4.
TDS_CLASSES: tuple[tuple[str, float], ...] = (
    ("Doce", 500.0),      # 0 – 500
    ("Salobra", 1500.0),  # 500 – 1500
    ("Salgada", 35000.0), # 1500 – 35000
    ("Salmoura", float("inf")),  # > 35000 (ex.: águas marinhas)
)

# --- Irrigação: USSL (Richards, 1954) ------------------------------------------------
# Risco de sódio (S) por SAR — (rótulo, limite_superior_exclusive).
USSL_S_THRESHOLDS: tuple[tuple[str, float], ...] = (
    ("S1", 10.0),
    ("S2", 18.0),
    ("S3", 26.0),
    ("S4", float("inf")),
)
# Risco de salinidade (C) por CE (µS/cm) — (rótulo, limite_superior_exclusive).
# QualiGraf inclui a classe C0 (< 100 µS/cm); ver Tutorial pág. 14.
# ATENÇÃO: no USSL original as classes de sódio (S) são retas dependentes da CE;
# aqui usamos limiares fixos de SAR como APROXIMAÇÃO (ver research.md §4).
USSL_C_THRESHOLDS: tuple[tuple[str, float], ...] = (
    ("C0", 100.0),
    ("C1", 250.0),
    ("C2", 750.0),
    ("C3", 2250.0),
    ("C4", float("inf")),
)

# --- IQA (CETESB) --------------------------------------------------------------------
# Pesos wi do produtório ponderado (Σ = 1.00). Fonte: CETESB.
IQA_WEIGHTS: dict[str, float] = {
    "do_sat": 0.17,        # Oxigênio Dissolvido (% saturação)
    "coliforms": 0.15,     # Coliformes termotolerantes (NMP/100mL)
    "ph": 0.12,            # pH
    "bod": 0.10,           # DBO5,20 (mg/L)
    "temp_var": 0.10,      # Variação de temperatura (°C)
    "n_total": 0.10,       # Nitrogênio total (mg/L)
    "p_total": 0.10,       # Fósforo total (mg/L)
    "turbidity": 0.08,     # Turbidez (UNT)
    "total_solids": 0.08,  # Resíduo/Sólidos totais (mg/L)
}

# Faixas de classificação IQA — (rótulo, limite_inferior_inclusive, limite_superior_excl).
# Valores EXATOS lidos da tela do QualiGraf (Figura 01 / Tutorial pág. 11).
# CETESB: Ótimo 80≤IQA≤100 · Bom 52≤IQA<80 · Aceitável 37≤IQA<52 · Ruim 20≤IQA<37 ·
#         Péssima 0≤IQA<20.
IQA_RANGES_CETESB: tuple[tuple[str, float, float], ...] = (
    ("Péssima", 0.0, 20.0),
    ("Ruim", 20.0, 37.0),
    ("Aceitável", 37.0, 52.0),
    ("Bom", 52.0, 80.0),
    ("Ótimo", 80.0, 100.0001),
)
# IGAM/MG: Excelente 90<IQA≤100 · Bom 70<IQA≤90 · Médio 50<IQA≤70 · Ruim 25<IQA≤50 ·
#          Muito Ruim 0<IQA≤25. (limite superior inclusivo → +ε no limite alto)
IQA_RANGES_IGAM: tuple[tuple[str, float, float], ...] = (
    ("Muito Ruim", 0.0, 25.0001),
    ("Ruim", 25.0001, 50.0001),
    ("Médio", 50.0001, 70.0001),
    ("Bom", 70.0001, 90.0001),
    ("Excelente", 90.0001, 100.0001),
)

# --- Mapeamento de aliases de colunas -> campos do WaterSample -----------------------
COLUMN_ALIASES: dict[str, str] = {
    "label": "label", "id": "label", "amostra": "label", "sample": "label", "ponto": "label",
    "ca": "ca", "ca2+": "ca", "calcio": "ca", "cálcio": "ca",
    "mg": "mg", "mg2+": "mg", "magnesio": "mg", "magnésio": "mg",
    "na": "na", "na+": "na", "sodio": "na", "sódio": "na",
    "k": "k", "k+": "k", "potassio": "k", "potássio": "k",
    "cl": "cl", "cl-": "cl", "cloreto": "cl",
    "so4": "so4", "so42-": "so4", "sulfato": "so4",
    "hco3": "hco3", "hco3-": "hco3", "bicarbonato": "hco3",
    "co3": "co3", "co32-": "co3", "carbonato": "co3",
    "no3": "no3", "nitrato": "no3",
    "ec": "ec", "ce": "ec", "condutividade": "ec", "cond": "ec",
    "ph": "ph",
    "tds": "tds", "std": "tds", "sdt": "tds",
    "temp": "temp", "temperatura": "temp",
    "temp_var": "temp_var", "variacao_temp": "temp_var",
    "do_sat": "do_sat", "od": "do_sat", "od_sat": "do_sat", "oxigenio": "do_sat",
    "bod": "bod", "dbo": "bod",
    "coliforms": "coliforms", "coliformes": "coliforms", "coli": "coliforms",
    "n_total": "n_total", "nitrogenio": "n_total", "nitrogênio": "n_total", "ntotal": "n_total",
    "p_total": "p_total", "fosforo": "p_total", "fósforo": "p_total", "ptotal": "p_total",
    "turbidity": "turbidity", "turbidez": "turbidity",
    "total_solids": "total_solids", "solidos_totais": "total_solids", "residuo": "total_solids",
    "lat": "lat", "latitude": "lat",
    "lon": "lon", "long": "lon", "longitude": "lon",
}
