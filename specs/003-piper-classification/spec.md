# Feature Specification: Classificação Hill-Piper + Projeção Correta do Losango

**Feature Branch**: `spec/003-piper-classification`

**Created**: 2026-09-04

**Status**: Draft (spec-first — aguarda aprovação antes da implementação)

**Input**: Corrigir a projeção do losango (diamond) do diagrama de Piper — hoje ad-hoc/
incorreta (spec 001, US5) — e adicionar a **classificação hidroquímica Hill-Piper** das
amostras (tipo de água), que o QualiGraf exibe (Tutorial pág. 16: "mostra a classificação
das amostras... distribuição percentual das amostras nos diversos campos").

> Dependência: assume a constituição v1.1.0 e o fluxo do PR #1 (spec 002). PRs independentes.

## Contexto

O diagrama de Piper tem dois triângulos (cátions Ca–Mg–Na+K; ânions HCO₃+CO₃–SO₄–Cl) e um
**losango central** onde cada amostra é projetada. A projeção atual em `diagrams.plot_piper`
usa uma fórmula improvisada (dúvida registrada na spec 001) — os pontos do losango caem em
posições erradas, o que também inviabiliza classificar por posição. Esta feature entrega a
geometria correta e a classificação por campos (facies).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Losango de Piper geometricamente correto (Priority: P1) 🎯 MVP

O ponto de cada amostra no losango resulta da projeção padrão dos pontos dos dois
triângulos (linhas paralelas às bordas do losango; interseção). Águas de tipo conhecido
caem no campo esperado.

**Why this priority**: Sem a geometria correta o diagrama de Piper é enganoso e nenhuma
classificação por posição é confiável.

**Independent Test**: uma água pura Ca-HCO₃ (só Ca e HCO₃) deve cair no **vértice inferior**
do losango; uma água Na-Cl pura, no **vértice direito**; verificável por coordenadas.

**Acceptance Scenarios**:
1. **Given** amostra 100% Ca / 100% HCO₃, **When** projeto no losango, **Then** o ponto
   cai no vértice inferior (dentro de tolerância).
2. **Given** amostra 100% Na+K / 100% Cl, **When** projeto, **Then** cai no vértice direito.
3. **Given** qualquer amostra, **When** projeto, **Then** o ponto fica **dentro** do losango.

---

### User Story 2 - Classificação hidroquímica (tipo de água) (Priority: P1)

Para cada amostra, obter a **facies catiônica** (Ca / Mg / Na+K / mista), a **facies
aniônica** (HCO₃ / SO₄ / Cl / mista) e o **tipo de água** resultante (ex.: `Ca-HCO₃`,
`Na-Cl`, `Mista`), além do **campo do losango** (dureza temporária / permanente /
alcalina-carbonatada / não-carbonatada / mista).

**Why this priority**: é a informação interpretativa central do Piper que o QualiGraf mostra.

**Independent Test**: `qualigraf piper amostras.csv` → tabela com facies e tipo; conferir
uma água Ca-HCO₃ conhecida.

**Acceptance Scenarios**:
1. **Given** %Ca>50 e %HCO₃>50, **When** classifico, **Then** tipo = `Ca-HCO₃`, campo do
   losango = "alcalino-terrosos + ácidos fracos (dureza temporária)".
2. **Given** nenhuma componente >50% em um triângulo, **When** classifico, **Then** a
   facies daquele lado é "mista" e o tipo reflete isso.
3. **Given** dados faltando um íon principal, **When** classifico, **Then** erro/aviso
   explícito (Princípio V).

---

### User Story 3 - Distribuição por campos + zonas no gráfico (Priority: P2)

O usuário vê a **distribuição percentual** das amostras nos campos do losango (tabela) e
pode sobrepor as **linhas das zonas** de classificação no diagrama.

**Independent Test**: `qualigraf piper amostras.csv --json` traz a contagem/percentual por
campo; `plot piper --zones` desenha as divisões.

**Acceptance Scenarios**:
1. **Given** N amostras, **When** peço a distribuição, **Then** recebo contagem e % por campo.
2. **Given** `--zones`, **When** gero o Piper, **Then** as linhas dos campos aparecem.

### Edge Cases
- Amostra sem cátions ou sem ânions → tipo indefinido, reportado (não quebra).
- Empate (ex.: %Ca=%Mg=50) → regra de desempate documentada (ex.: "mista").
- As zonas exatas do QualiGraf não estão publicadas → usar esquema padrão e **validar**
  contra o software (task), como fizemos com IQA/USSL.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-301**: O sistema DEVE projetar cada amostra no losango de Piper pela geometria
  padrão (projeção dos pontos dos triângulos de cátions e ânions), substituindo a fórmula
  atual de `plot_piper`.
- **FR-302**: O sistema DEVE classificar cada amostra em: facies catiônica, facies
  aniônica, tipo de água (cátion-ânion dominantes) e campo do losango (facies de Piper).
- **FR-303**: A dominância DEVE usar limiar de 50% (meq) por padrão, com regra de
  desempate documentada; limiares configuráveis (constantes nomeadas).
- **FR-304**: O sistema DEVE calcular a distribuição (contagem e %) das amostras por campo.
- **FR-305**: A classificação DEVE ser exposta na CLI (`qualigraf piper`, tabela + `--json`)
  e no app (tabela na aba de Diagramas).
- **FR-306**: `plot piper` DEVE oferecer sobreposição opcional das zonas de classificação
  (`--zones`).
- **FR-307**: As zonas/limiares DEVEM citar a fonte (Piper 1944 / Hill 1940) e ficar
  marcados como "a validar contra o QualiGraf" enquanto não confirmados.

### Key Entities
- **PiperClassification**: label, cation_facies, anion_facies, water_type, diamond_field,
  pct por triângulo (opcional). Serializável para JSON.

## Success Criteria *(mandatory)*

- **SC-301**: Águas-teste (Ca-HCO₃, Na-Cl, Ca-Cl, Na-HCO₃) caem no campo correto do
  losango e recebem o tipo esperado (100% dos casos de referência).
- **SC-302**: Todo ponto projetado fica dentro do losango.
- **SC-303**: `qualigraf piper` roda em uma planilha de exemplo e retorna facies+tipo por
  amostra + distribuição por campos.

## Assumptions
- Esquema de classificação: dominância >50% nos triângulos e os 4 campos clássicos do
  losango (alcalino-terrosos×alcalinos × ácidos fracos×fortes) + centro "mista". Fonte:
  Piper (1944), Hill (1940). Boundaries exatas do QualiGraf a validar (task).
- Escopo: classificação e geometria; **não** inclui salvar a "tabela anexa" do QualiGraf
  pixel-a-pixel, apenas os dados equivalentes.
