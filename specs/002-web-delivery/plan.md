# Implementation Plan: Camada de Entrega — App Web + Unidades

**Branch**: `spec/002-web-delivery` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

## Summary

Camada de entrega sobre a biblioteca `hidrograf` (spec 001): app Streamlit publicado no
Streamlit Cloud, upload com detecção/escolha de unidade (mg/L, meq/L) normalizando para
mg/L, e diagramas expansíveis com download (PNG/SVG/ZIP). Inclui a disciplina de deploy
(feature branch → PR → merge na `main` = produção). Documento de reconciliação: a maior
parte já foi construída; o plano registra a arquitetura e o débito remanescente.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: streamlit, matplotlib, pandas, numpy, openpyxl (via `hidrograf`)
**Storage**: sem estado; uploads processados em memória / `/tmp` efêmero
**Testing**: pytest (glue da web — pendente, FR-207)
**Target Platform**: Streamlit Community Cloud (navegador)
**Project Type**: library + CLI (spec 001) + **web UI** (esta spec)
**Deploy**: push na `main` → redeploy automático; entrada na `main` só via PR

## Constitution Check

*GATE.* A constituição foi emendada (v1.1.0): web/UI deixou de ser "fora de escopo";
adicionados os princípios de **Entrega/Deploy** (spec-first, branch+PR).

| Princípio | Conformidade |
|-----------|--------------|
| I. Library-First, Domain-Pure | ✅ a UI só importa `hidrograf`; zero cálculo na UI |
| II. CLI Interface | ✅ mantida; `--unit` adicionado |
| III. Test-First numérico | 🟡 cálculos testados; **glue da web sem testes** (FR-207) |
| IV. Traceabilidade científica | ✅ inalterada |
| V. Dados explícitos | ✅ erros de unidade/inválidos reportados |
| VI. Entrega spec-first + PR (novo) | 🟡 adotado a partir deste PR |

## Project Structure

```text
streamlit_app.py            # UI (importa hidrograf)
requirements.txt            # deps do app (Streamlit Cloud)
.streamlit/config.toml      # tema/headless
DEPLOY.md                   # como publicar
CONTRIBUTING.md             # fluxo spec-first + branch/PR (novo)
src/hidrograf/io.py         # detect_ion_units + load(default_unit)
src/hidrograf/cli.py        # --unit em balance/sar/convert
tests/test_io.py            # testes de unidade (mg/meq)
tests/test_web.py           # glue da web (PENDENTE, FR-207)
```

**Structure Decision**: a UI é um único arquivo raiz que adiciona `src/` ao path e importa
a biblioteca — mantém a separação cálculo/interface da constituição.

## Complexity Tracking

| Desvio | Por que | Alternativa rejeitada |
|--------|---------|-----------------------|
| Features entregues antes desta spec | Pedidos interativos do usuário; velocidade | Idealmente spec-first; corrigido por esta reconciliação e pelo gate de PR |
