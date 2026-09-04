# Implementation Plan: Classificação Hill-Piper + Losango Correto

**Branch**: `spec/003-piper-classification` | **Date**: 2026-09-04 | **Spec**: [spec.md](./spec.md)

## Summary

Corrigir a projeção do losango de Piper (geometria padrão) e adicionar a classificação
hidroquímica Hill-Piper (facies catiônica/aniônica, tipo de água, campo do losango) +
distribuição por campos, expostas na biblioteca, CLI e app. Depende de `geometry.py`
(coordenadas ternárias, já existente) e de `chemistry`/`models` (meq/L).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: numpy, matplotlib (já no projeto)
**Testing**: pytest — testes de geometria (vértices/dentro do losango) e de classificação
(águas-teste sintéticas com tipo conhecido)
**Project Type**: library + CLI + web (specs 001/002)
**Constraints**: cálculo puro em `qualigraf.*` (Princípio I); constantes nomeadas com fonte
(Princípio IV)

## Constitution Check

| Princípio | Conformidade |
|-----------|--------------|
| I. Library-First | ✅ classificação/geometria puras; plot só desenha |
| III. Test-First | ✅ testes de valor-fixado (vértices do losango, águas-teste) antes/junto |
| IV. Traceabilidade | ✅ zonas citam Piper 1944/Hill 1940; marcadas "a validar" |
| V. Dados explícitos | ✅ tipo indefinido reportado quando faltam íons |
| VI. Spec-first + PR | ✅ esta spec precede o código; entrega via PR |

## Abordagem técnica

### 1. Projeção correta do losango (FR-301)
- Cátions: a=Ca, b=Na+K, c=Mg (% de meq). Ânions: a=HCO₃+CO₃, b=Cl, c=SO₄.
- Projetar o ponto do triângulo de cátions e o do triângulo de ânions para o losango ao
  longo de retas paralelas às bordas; a **interseção** é o ponto no losango. Fórmula
  fechada padrão (converter (%Na+K, %Cl) etc. para coordenadas do losango).
- Implementar em `geometry.py`: `piper_diamond_xy(cation_pcts, anion_pcts) -> (x, y)`.
- Testar com vértices: Ca-HCO₃→inferior, Na-Cl→direito, Ca-Cl→superior, Na-HCO₃→esquerdo;
  e invariante "dentro do losango".

### 2. Classificação (FR-302/303)
- Novo módulo `piper.py`: `classify_sample(s) -> PiperClassification`.
- Facies por dominância >50% (constantes `PIPER_DOMINANCE = 50.0`); desempate → "mista".
- Campo do losango pelas metades: alcalino-terrosos (Ca+Mg) vs alcalinos (Na+K); ácidos
  fracos (HCO₃+CO₃) vs fortes (SO₄+Cl); 4 quadrantes + centro "mista".
- `PiperClassification` em `models.py` (com `to_dict`).

### 3. Distribuição + zonas (FR-304/306)
- `piper.field_distribution(samples) -> {campo: (n, pct)}`.
- `diagrams.plot_piper(..., zones=False)`: desenhar as linhas dos campos quando `zones`.

### 4. Superfícies de exposição (FR-305)
- CLI: `qualigraf piper FILE [--unit] [--json] [-o]`.
- App: tabela de classificação na aba Diagramas + checkbox "mostrar zonas".

## Project Structure

```text
src/qualigraf/geometry.py   # + piper_diamond_xy()
src/qualigraf/piper.py      # NOVO: classify_sample, field_distribution
src/qualigraf/models.py     # + PiperClassification
src/qualigraf/diagrams.py   # plot_piper: projeção correta + zones
src/qualigraf/cli.py        # + comando `piper`
streamlit_app.py            # tabela de classificação + zonas
tests/test_geometry.py      # + vértices/dentro do losango
tests/test_piper.py         # NOVO: águas-teste, facies, tipo, distribuição
```

## Complexity Tracking
*Sem violações previstas.* Boundaries exatas do QualiGraf ficam como task de validação
(não bloqueiam): usar esquema padrão citado e validar depois.
