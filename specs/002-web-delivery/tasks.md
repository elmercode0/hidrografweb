# Tasks: Camada de Entrega — App Web + Unidades

**Input**: `specs/002-web-delivery/` (spec, plan). Reconciliação: itens já construídos
marcados [x]; pendências reais marcadas [ ].

## Format: `[ID] [P?] [Story] Descrição`

## Phase 1: App web (US1) — construído

- [x] T201 [US1] `streamlit_app.py` importando `qualigraf` (src no path, matplotlib Agg)
- [x] T202 [US1] Abas: Dados, Balanço, STD, SAR, IQA, Estatísticas, Correlação, Diagramas
- [x] T203 [US1] Upload CSV/XLSX + dados de exemplo + tratamento de `DataError`
- [x] T204 [US1] `requirements.txt`, `.streamlit/config.toml`, `DEPLOY.md`

## Phase 2: Unidades mg/L e meq/L (US2) — construído

- [x] T205 [US2] `io._split_header` + `io.detect_ion_units` (detecção por cabeçalho)
- [x] T206 [US2] `io.load(default_unit)` normaliza íons meq→mg; `Mg` não confundido
- [x] T207 [US2] Seletor de unidade no upload (pré-seleção pela detecção; exige escolha se ausente)
- [x] T208 [US2] CLI `--unit mg|meq` em `balance`/`sar`/`convert`
- [x] T209 [P] [US2] `tests/test_io.py` — detecção, conversão meq→mg, precedência, `Mg`

## Phase 3: Diagramas — expandir + download (US3) — construído

- [x] T210 [US3] `st.image` com expandir em tela cheia; seletor de DPI (150/200/300/600)
- [x] T211 [US3] Download por diagrama (PNG alta-res + SVG) e ZIP com todos
- [x] T212 [US3] Render cacheado (`st.cache_data`), figuras fechadas (sem vazamento)

## Phase 4: Gate de produção (US4) — processo

- [x] T213 [US4] Este trabalho numa feature branch + PR (modela o gate)
- [x] T214 [US4] `CONTRIBUTING.md` com o fluxo spec-first + branch/PR = deploy
- [x] T215 [US4] Constituição emendada (v1.1.0): web em escopo + princípio de entrega
- [ ] T216 [US4] (opcional) Proteção da branch `main` no GitHub exigindo PR

## Phase 5: Pendências (débito técnico honesto)

- [ ] T217 [P] [US2/US3] `tests/test_web.py` — testar a "cola" da UI sem navegador:
      carga mg/meq, `detect_ion_units`, render de diagrama → PNG/SVG válidos (FR-207/SC-204)
- [x] T218 [P] `tests/data/sample_waters_meq.csv` — exemplo em meq/L p/ testes/demonstração
- [ ] T219 [P] (opcional) CI (GitHub Actions) rodando pytest+ruff em cada PR

## Dependências
- US1/US2/US3 concluídas. US4 é processo (vigente a partir deste PR).
- Pendências (Phase 5) são independentes e podem ser feitas em PRs próprios.
