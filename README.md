# Hidrograf

Reimplementação em Python (biblioteca + CLI) dos módulos de análise hidroquímica do
**QualiGraf** da [FUNCEME](http://www.funceme.br/). Gerado via fluxo *spec-driven*
([spec-kit](https://github.com/github/spec-kit)) a partir do dump do site em `scrapling/`.

Especificação completa em [`specs/001-qualigraf-core/`](specs/001-qualigraf-core/).

## Módulos

| Análise | Comando | Descrição |
|---------|---------|-----------|
| Balanço iônico | `balance` | meq/L por íon, ΣCátions/ΣÂnions, erro prático Ep% (somatórios e CE) |
| Sólidos Totais Dissolvidos | `tds` | STD = CE×0,65 (ou medido) + classe CONAMA 357/2005 |
| Irrigação SAR/USSL | `sar` | SAR = Na/√((Ca+Mg)/2) + classe USSL (C1–C4 × S1–S4) |
| IQA | `iqa` | Índice de Qualidade da Água (produtório CETESB) + faixas CETESB/IGAM |
| Estatísticas | `stats` | n, mín, máx, média, variância, desvio-padrão |
| Correlação | `correlate` | ajuste por mínimos quadrados + R² |
| Diagramas | `plot {piper\|stiff\|durov\|schoeller\|radial}` | diagramas hidroquímicos em PNG/SVG |
| Conversão | `convert` | mg/L ↔ meq/L de uma planilha |

## Instalação

```bash
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Uso

Veja [`specs/001-qualigraf-core/quickstart.md`](specs/001-qualigraf-core/quickstart.md).

```bash
hidrograf balance tests/data/sample_waters.csv --method both
hidrograf iqa tests/data/sample_waters.csv --json
hidrograf plot piper tests/data/sample_waters.csv -o piper.png --labels
```

## Testes

```bash
pytest -q
```

## Validação (dúvidas resolvidas)

Todas as dúvidas da auditoria foram resolvidas com fontes autoritativas — ver
`specs/001-qualigraf-core/research.md` para fórmulas e citações:

- **IQA**: 9 curvas qi **digitalizadas da Figura 01** e validadas contra o exemplo
  resolvido do QualiGraf (**8/9 âncoras conferem**, ±2–3 q) e contra as **equações oficiais
  CETESB** (BasIQA 2013). **DBO resolvido**: a eq. `q=102,6·exp(−0,1101·DBO)` dá ≈20 =
  nossa curva; o 67,57 da tela do QualiGraf é **bug de exibição** do software. Faixas
  CETESB/IGAM são os valores exatos da tela.
- **Balanço iônico**: fórmula **Custódio & Llamas (1983)** (antes estava pela metade);
  aceitação por **CE (Custódio & Llamas)** e por **soma de íons (Logan 1965)**.
- **USSL**: limiares de sódio 10/18/26 são o padrão categórico (Richards 1954/Handbook 60).
- **OD**: conversão mg/L → %saturação via `chemistry.do_saturation_pct` (APHA).
- **STD/CONAMA**: tabela do Tutorial (Doce/Salobra/Salgada/Salmoura).

## Limitações (v1)

- Alguns coeficientes das equações CETESB vêm de OCR (conferir antes de usá-las no lugar
  das curvas digitalizadas). Validação ampla exigiria rodar o QualiGraf (Windows) — as
  curvas + equações CETESB tornam isso opcional.
- **Unidades**: íons em **mg/L ou meq/L** — detectadas pelo cabeçalho (`Na (meq/L)`) ou
  informadas (`--unit` na CLI / seletor no app); normalizadas para mg/L internamente. CE
  sempre em µS/cm.
- Fora do escopo: GUI desktop, Google Maps/editores, impressão direta ("Miscelânea").
- Reproduz os cálculos e a semântica dos módulos, não o layout visual pixel-a-pixel.

Baseado no QualiGraf © FUNCEME. Esta é uma reimplementação independente para fins de
estudo/uso programático.
