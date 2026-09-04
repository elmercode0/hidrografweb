# Quickstart — Hidrograf

## Instalação (dev)

```bash
cd /Users/elmerrodrigues/code/active/hidrografweb
uv venv && source .venv/bin/activate      # ou: python3.11 -m venv .venv
uv pip install -e ".[dev]"                 # ou: pip install -e ".[dev]"
```

## Formato da planilha

CSV/XLSX com uma amostra por linha. Cabeçalhos reconhecidos por aliases
(ex.: `Na`, `Sodio`, `Na+`).

> **Unidades dos íons — mg/L ou meq/L:** detectadas pelo cabeçalho quando indicadas
> (`Na (meq/L)`, `Cl_mg/L`, `SO4 (epm)`); onde não houver, informe a unidade — na CLI com
> `--unit mg|meq`, no app com o seletor do upload. Tudo é normalizado para mg/L
> internamente. **CE sempre em µS/cm** (sem conversão automática de dS/m — daria 1000×
> errado). Para o IQA, `OD` deve ser **% de saturação** (use `chemistry.do_saturation_pct`
> se tiver mg/L) e `temp_var` é a **variação** de temperatura. Células não numéricas são
> rejeitadas com erro citando a amostra.

```csv
label,Ca,Mg,Na,K,Cl,SO4,HCO3,CO3,EC,pH,TDS
P1,40,12,25,3,30,20,150,0,600,7.2,
P2,80,30,120,8,180,90,200,0,1800,7.8,
```

## Uso rápido

```bash
hidrograf balance tests/data/sample_waters.csv          # tabela no terminal
hidrograf tds tests/data/sample_waters.csv --json       # JSON
hidrograf sar tests/data/sample_waters.csv
hidrograf iqa tests/data/sample_waters.csv
hidrograf stats tests/data/sample_waters.csv
hidrograf correlate tests/data/sample_waters.csv --x Cl --y Na
hidrograf plot piper tests/data/sample_waters.csv -o piper.png --labels
```

## Uso como biblioteca

```python
from hidrograf.io import load
from hidrograf.balance import ionic_balance
from hidrograf.diagrams import plot_piper

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
