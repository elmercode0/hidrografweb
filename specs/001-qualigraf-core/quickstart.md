# Quickstart — QualiGraf-Py

## Instalação (dev)

```bash
cd /Users/elmerrodrigues/code/active/qualigrafweb
uv venv && source .venv/bin/activate      # ou: python3.11 -m venv .venv
uv pip install -e ".[dev]"                 # ou: pip install -e ".[dev]"
```

## Formato da planilha

CSV/XLSX com uma amostra por linha. Cabeçalhos reconhecidos por aliases
(ex.: `Na`, `Sodio`, `Na+`).

> ⚠️ **Unidades obrigatórias (v1):** íons em **mg/L** e CE em **µS/cm**. Não há conversão
> automática — CE em dS/m ou mS/cm produz STD e classe USSL **1000× errados**. Para o IQA,
> `OD` deve ser **% de saturação** (não mg/L) e `temp_var` é a **variação** de temperatura.
> Células não numéricas são rejeitadas com erro citando a amostra (não são descartadas).

```csv
label,Ca,Mg,Na,K,Cl,SO4,HCO3,CO3,EC,pH,TDS
P1,40,12,25,3,30,20,150,0,600,7.2,
P2,80,30,120,8,180,90,200,0,1800,7.8,
```

## Uso rápido

```bash
qualigraf balance tests/data/sample_waters.csv          # tabela no terminal
qualigraf tds tests/data/sample_waters.csv --json       # JSON
qualigraf sar tests/data/sample_waters.csv
qualigraf iqa tests/data/sample_waters.csv
qualigraf stats tests/data/sample_waters.csv
qualigraf correlate tests/data/sample_waters.csv --x Cl --y Na
qualigraf plot piper tests/data/sample_waters.csv -o piper.png --labels
```

## Uso como biblioteca

```python
from qualigraf.io import load
from qualigraf.balance import ionic_balance
from qualigraf.diagrams import plot_piper

samples = load("tests/data/sample_waters.csv")
for r in ionic_balance(samples, method="both"):
    print(r.label, r.ep_sum)

fig = plot_piper(samples, labels=True)
fig.savefig("piper.png", dpi=150)
```

## Testes

```bash
pytest -q          # todos os testes de valor-fixado devem passar
ruff check src     # lint
```
