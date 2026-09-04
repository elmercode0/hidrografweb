# Tasks: Classificação Hill-Piper + Losango Correto

**Input**: `specs/003-piper-classification/` (spec, plan). **Spec-first**: nada de código
antes da aprovação desta spec. Todas as tasks abaixo estão pendentes `[ ]`.

## Format: `[ID] [P?] [Story] Descrição`

## Phase 1: Geometria do losango (US1) 🎯 MVP

- [ ] T301 [US1] `geometry.piper_diamond_xy(cation_pcts, anion_pcts)` — projeção padrão
      (retas paralelas às bordas; interseção). Coordenadas coerentes com os triângulos.
- [ ] T302 [P] [US1] `tests/test_geometry.py` — vértices (Ca-HCO₃→inferior, Na-Cl→direito,
      Ca-Cl→superior, Na-HCO₃→esquerdo) e invariante "ponto dentro do losango".
- [ ] T303 [US1] `diagrams.plot_piper`: substituir a projeção ad-hoc do losango pela nova
      (remover a fórmula marcada como dúvida na spec 001).

## Phase 2: Classificação (US2)

- [ ] T304 [US2] `models.PiperClassification` (label, cation_facies, anion_facies,
      water_type, diamond_field, pcts) + `to_dict`.
- [ ] T305 [US2] `piper.classify_sample` — facies por dominância >50% (constante
      `PIPER_DOMINANCE`), tipo de água, campo do losango; desempate → "mista".
- [ ] T306 [US2] `constants.py` — limiares/rotulos dos campos citando Piper 1944 / Hill 1940
      (marcados "a validar contra o QualiGraf").
- [ ] T307 [P] [US2] `tests/test_piper.py` — águas-teste sintéticas (Ca-HCO₃, Na-Cl,
      Ca-Cl, Na-HCO₃, mista) → facies/tipo/campo esperados; caso sem íons → indefinido.

## Phase 3: Distribuição + exposição (US3)

- [ ] T308 [US3] `piper.field_distribution(samples)` — contagem e % por campo.
- [ ] T309 [US3] CLI `qualigraf piper FILE [--unit] [--json] [-o]` (tabela + JSON).
- [ ] T310 [US3] `plot_piper(..., zones=True)` desenha as linhas dos campos.
- [ ] T311 [US3] App: tabela de classificação na aba Diagramas + checkbox "mostrar zonas".
- [ ] T312 [P] [US3] `tests/test_piper.py` — distribuição por campos; smoke da CLI `piper`.

## Phase 4: Validação (débito de fidelidade)

- [ ] T313 [P] Validar zonas/tipos contra o QualiGraf real (quando possível rodar o .exe)
      ou literatura adicional; ajustar boundaries e remover a marca "a validar".

## Dependências
- US1 (geometria) antecede US3 (zonas no gráfico). US2 (classificação) usa a mesma
  matemática de %meq, independente do desenho.
- Entregar via PR (gate de produção). Sugerido: um PR para US1+US2 (MVP) e outro para US3,
  ou um único PR se preferir.
