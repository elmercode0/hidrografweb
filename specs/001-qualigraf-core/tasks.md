# Tasks: QualiGraf-Py — Núcleo de Análise Hidroquímica

**Input**: Design em `/specs/001-qualigraf-core/` (plan, spec, research, data-model, contracts)

**Tests**: incluídos — a constituição exige teste de valor-fixado por módulo de cálculo.

**Organização**: por user story; cada story é um incremento MVP independente.

## Format: `[ID] [P?] [Story] Descrição`
- **[P]**: paralelizável (arquivo distinto, sem dependência)

## Phase 1: Setup (infra compartilhada)

- [x] T001 Criar `pyproject.toml` (PEP 621, src layout, deps: numpy/pandas/matplotlib/typer/openpyxl; extra dev: pytest/ruff) e `src/qualigraf/__init__.py`
- [x] T002 [P] Configurar `ruff` e seção `pytest` em `pyproject.toml`
- [x] T003 [P] Criar `tests/data/sample_waters.csv` com amostras de referência

## Phase 2: Foundational (bloqueante — antes de qualquer story)

- [x] T004 Implementar `src/qualigraf/constants.py` (pesos equiv., fatores, pesos IQA, limiares CONAMA/USSL/IQA, aliases de colunas) — ver research.md
- [x] T005 Implementar `src/qualigraf/models.py` (WaterSample, SampleSet, dataclasses *Result com to_dict)
- [x] T006 Implementar `src/qualigraf/chemistry.py` (mg/L↔meq/L) + `tests/test_chemistry.py`
- [x] T007 Implementar `src/qualigraf/io.py` (load CSV/XLSX, mapeamento de aliases, validação)
- [x] T008 Esqueleto do `src/qualigraf/cli.py` (typer app, helpers de saída tabela/JSON, tratamento de erro)

**Checkpoint**: fundação pronta — stories podem começar.

## Phase 3: US1 Balanço Iônico (P1) 🎯 MVP

- [x] T009 [US1] Implementar `src/qualigraf/balance.py` (meq/íon, ΣCát, ΣÂn, Ep% sum e ec)
- [x] T010 [US1] Comando `balance` na CLI (--method sum|ec|both, --json)
- [x] T011 [P] [US1] `tests/test_balance.py` — Ep% contra caso calculado à mão (SC-001)

**Checkpoint**: US1 funcional e testável isoladamente.

## Phase 4: US2 STD + CONAMA (P1)

- [x] T012 [US2] Implementar `src/qualigraf/tds.py` (STD=CE×fator ou medido; classe CONAMA)
- [x] T013 [US2] Comando `tds` na CLI (--factor, --json)
- [x] T014 [P] [US2] `tests/test_tds.py` — estimativa, precedência do medido, classes (SC-002)

## Phase 5: US3 SAR + USSL (P2)

- [x] T015 [US3] Implementar `src/qualigraf/irrigation.py` (SAR + classes C/S + rótulo USSL)
- [x] T016 [US3] Comando `sar` na CLI (--json)
- [x] T017 [P] [US3] `tests/test_irrigation.py` — SAR à mão + rótulos USSL (SC-002); Ca+Mg=0 → indefinido

## Phase 6: US4 IQA (P2)

- [x] T018 [US4] Implementar `src/qualigraf/iqa_curves.py` (pontos das curvas qi CETESB + interpolação)
- [x] T019 [US4] Implementar `src/qualigraf/iqa.py` (produtório ponderado; erro se faltar parâmetro; classes CETESB+IGAM)
- [x] T020 [US4] Comando `iqa` na CLI (--json)
- [x] T021 [P] [US4] `tests/test_iqa.py` — IQA de referência + erro por parâmetro ausente

## Phase 7: US5 Diagramas (P2)

- [x] T022 [US5] Implementar `src/qualigraf/geometry.py` (coordenadas ternárias) + `tests/test_geometry.py`
- [x] T023 [US5] Implementar `src/qualigraf/diagrams.py` (plot_piper/stiff/durov/schoeller/radial → Figure)
- [x] T024 [US5] Comando `plot {tipo}` na CLI (-o, --labels, --select)
- [x] T025 [P] [US5] `tests/test_diagrams.py` — cada plot gera arquivo não vazio (SC-003)

## Phase 8: US6 Estatísticas + Correlação (P3)

- [x] T026 [US6] Implementar `src/qualigraf/stats.py` (estatísticas básicas + correlação/R²)
- [x] T027 [US6] Comandos `stats` e `correlate` na CLI (--json)
- [x] T028 [P] [US6] `tests/test_stats.py` — média/dp e R² contra valores à mão

## Phase 9: Polish

- [x] T029 [P] `convert` na CLI (mg/L↔meq/L de planilha) + export .txt/.csv (FR-011)
- [x] T030 [P] `tests/test_cli.py` — smoke de cada comando (humano + --json)
- [x] T031 [P] README do projeto com base no quickstart.md

## Dependências
- Phase 2 bloqueia todas as stories. Dentro de cada story: modelo → CLI → testes [P].
- Stories US1–US6 são independentes entre si após a fundação.
