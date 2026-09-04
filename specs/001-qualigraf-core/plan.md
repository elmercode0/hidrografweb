# Implementation Plan: Hidrograf — Núcleo de Análise Hidroquímica

**Branch**: `001-qualigraf-core` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-qualigraf-core/spec.md`

## Summary

Biblioteca Python (`hidrograf`) de cálculos hidroquímicos puros + CLI (`typer`) que lê
planilhas de amostras (CSV/XLSX) e produz balanço iônico, STD/CONAMA, SAR/USSL, IQA
(CETESB+IGAM), estatísticas, correlações e os diagramas de Piper, Stiff, Durov,
Schoeller-Berkaloff e Radial. Cálculos são funções puras testadas contra valores de
referência; a CLI oferece saída humana e `--json`.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: numpy, pandas, matplotlib, typer; openpyxl (XLSX); pytest (dev), ruff (dev)
**Storage**: arquivos (CSV/XLSX de entrada; PNG/SVG/TXT/CSV de saída) — sem banco
**Testing**: pytest com testes de valor-fixado por módulo
**Target Platform**: multiplataforma (macOS/Linux/Windows), offline
**Project Type**: single project — library + CLI (`src/` layout)
**Performance Goals**: < 5 s por diagrama; planilhas de até ~10⁴ amostras sem degradação
**Constraints**: sem rede em runtime; toda constante científica nomeada e documentada
**Scale/Scope**: 9 módulos de análise + 5 diagramas; ~1 pacote, ~15 módulos

## Constitution Check

*GATE: pass antes da fase 0; re-check após design.*

| Princípio | Conformidade |
|-----------|--------------|
| I. Library-First, Domain-Pure | ✅ cálculos em `hidrograf/*` sem I/O; CLI separada |
| II. CLI Interface | ✅ toda análise na CLI com tabela + `--json` |
| III. Test-First numérico | ✅ tasks de teste de valor-fixado precedem/acompanham cada módulo |
| IV. Traceabilidade científica | ✅ constantes nomeadas + fontes em `constants.py`/docstrings (ver research.md) |
| V. Dados explícitos | ✅ validação por análise, erros nomeando campo/amostra |

**Resultado**: PASS. Sem violações → Complexity Tracking vazio.

## Project Structure

### Documentation (this feature)

```text
specs/001-qualigraf-core/
├── plan.md          # este arquivo
├── spec.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md       # contrato dos comandos da CLI
└── tasks.md         # gerado na fase de tasks
```

### Source Code (repository root)

```text
pyproject.toml
src/
└── hidrograf/
    ├── __init__.py
    ├── constants.py        # pesos equiv., fatores, pesos IQA, limiares de classes
    ├── models.py           # WaterSample, SampleSet, *Result (dataclasses)
    ├── io.py               # load CSV/XLSX + mapeamento de aliases de colunas
    ├── chemistry.py        # mg/L <-> meq/L
    ├── balance.py          # US1 balanço iônico
    ├── tds.py              # US2 STD + CONAMA
    ├── irrigation.py       # US3 SAR + USSL
    ├── iqa.py              # US4 IQA (usa iqa_curves)
    ├── iqa_curves.py       # pontos das curvas qi CETESB + interpolação
    ├── stats.py            # US6 estatísticas + correlação
    ├── geometry.py         # coordenadas ternárias (Piper/Durov)
    ├── diagrams.py         # US5 Piper/Stiff/Durov/Schoeller/Radial
    └── cli.py              # typer app: balance/tds/sar/iqa/stats/correlate/plot

tests/
├── data/
│   └── sample_waters.csv   # amostras de exemplo/referência
├── test_chemistry.py
├── test_balance.py
├── test_tds.py
├── test_irrigation.py
├── test_iqa.py
├── test_stats.py
├── test_geometry.py
├── test_diagrams.py
└── test_cli.py
```

**Structure Decision**: single project, `src/` layout. Uma story ↔ um módulo de análise,
cada um shippable de forma independente. `constants.py`, `models.py`, `io.py`,
`chemistry.py` são a fundação compartilhada (bloqueante) antes das stories.

## Complexity Tracking

*Sem violações da constituição — nada a justificar.*
