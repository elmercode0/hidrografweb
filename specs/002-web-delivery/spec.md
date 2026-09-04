# Feature Specification: Camada de Entrega — App Web + Empacotamento de Unidades

**Feature Branch**: `spec/002-web-delivery`

**Created**: 2026-09-04

**Status**: Reconciliação (documenta features já construídas fora do fluxo + pendências)

**Input**: App Streamlit publicado no Streamlit Cloud, upload com detecção de unidade
(mg/L, meq/L), diagramas expansíveis com download (PNG alta-res/SVG/ZIP). Esta spec
**reconcilia** o que foi implementado *implement-first* nos commits `7180caf`, `3ef1d32`,
`f278d2d`, trazendo-o para o fluxo spec-driven.

## Contexto e motivação

A spec `001-qualigraf-core` entregou a biblioteca + CLI e declarou GUI/web **fora do
escopo v1**. Depois, a pedido do usuário, foram adicionados: um app web (Streamlit),
upload com unidade configurável e download de diagramas — sem passar por spec/plan/tasks.
Esta feature documenta essa camada de entrega, ajusta o escopo (web agora é suportado) e
registra o débito técnico remanescente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Usar as análises no navegador (Priority: P1) — ✅ construído

Analista sobe uma planilha e vê, em abas, balanço iônico, STD/CONAMA, SAR/USSL, IQA,
estatísticas, correlação e diagramas — sem instalar nada.

**Independent Test**: abrir o app, ativar "dados de exemplo", navegar pelas abas.

**Acceptance Scenarios**:
1. **Given** uma planilha CSV/XLSX, **When** faço upload, **Then** cada aba mostra a
   respectiva análise usando a biblioteca `hidrograf`.
2. **Given** dados inválidos, **When** carrego, **Then** vejo erro claro (Princípio V).

---

### User Story 2 - Escolher/detectar a unidade dos íons (Priority: P1) — ✅ construído

O usuário sobe planilha em **mg/L ou meq/L**; a unidade é detectada pelo cabeçalho e,
quando ausente, ele a indica no upload.

**Independent Test**: subir planilha `Na (meq/L)` (auto) e outra sem unidade (seletor).

**Acceptance Scenarios**:
1. **Given** cabeçalho `Ca (meq/L)`, **When** carrego, **Then** a unidade é detectada e
   os valores normalizados para mg/L.
2. **Given** cabeçalho sem unidade, **When** carrego, **Then** o app exige a escolha
   mg/L ou meq/L.
3. **Given** coluna `Mg` (magnésio) sem unidade, **When** carrego, **Then** não é
   confundida com miligrama.

---

### User Story 3 - Ampliar e baixar diagramas (Priority: P2) — ✅ construído

O usuário expande o diagrama em tela cheia e baixa cada um separadamente em alta
resolução (PNG/SVG) ou todos em ZIP.

**Acceptance Scenarios**:
1. **Given** um diagrama, **When** clico no ícone de expandir, **Then** ele abre em tela
   cheia.
2. **Given** um diagrama, **When** escolho o DPI e clico em baixar, **Then** recebo o
   PNG/SVG correspondente; e um ZIP com todos.

---

### User Story 4 - Deploy contínuo com gate (Priority: P2) — 🔜 processo

Mudanças chegam à produção (Streamlit Cloud) apenas após passar pelo fluxo:
feature branch → spec/tasks → PR → merge na `main`.

**Acceptance Scenarios**:
1. **Given** uma mudança, **When** é feita, **Then** vai numa branch e um PR, nunca
   direto na `main`.
2. **Given** um PR aprovado, **When** faço merge na `main`, **Then** o Streamlit Cloud
   redeploya.

### Edge Cases
- Planilha só com parâmetros de IQA (sem íons) → seletor de unidade não aparece.
- XLSX além de CSV → ambos suportados.
- Sessão sem arquivo → app orienta a subir ou usar exemplo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-201**: O sistema DEVE oferecer uma UI web (Streamlit) que exponha todas as análises
  da biblioteca, sem exigir instalação pelo usuário final. *(construído)*
- **FR-202**: A UI DEVE aceitar upload CSV/XLSX e oferecer dados de exemplo. *(construído)*
- **FR-203**: O sistema DEVE detectar a unidade dos íons pelo cabeçalho (`meq`, `mg/L`,
  `epm`) e, quando ausente, permitir ao usuário indicá-la; normalizando para mg/L.
  *(construído — `io.detect_ion_units`, `io.load(default_unit)`, seletor no app)*
- **FR-204**: A UI DEVE permitir expandir cada diagrama em tela cheia e baixá-lo
  individualmente (PNG com DPI configurável e SVG) e todos em ZIP. *(construído)*
- **FR-205**: A CLI DEVE aceitar `--unit mg|meq` nos comandos que usam íons. *(construído)*
- **FR-206**: Mudanças DEVEM chegar à produção via feature branch + PR (sem push direto
  na `main`). *(processo — este PR é o primeiro exemplo)*
- **FR-207**: A camada web DEVE ter testes automatizados da sua "cola" (carga, unidades,
  render de diagramas). *(pendente)*

### Key Entities
Reutiliza as da spec 001. Adiciona apenas artefatos de entrega: `streamlit_app.py`
(UI), `requirements.txt`, `.streamlit/config.toml`, `DEPLOY.md`.

## Success Criteria *(mandatory)*

- **SC-201**: Um usuário processa uma planilha (mg/L **ou** meq/L) do upload ao diagrama
  baixado, sem editar código. *(atingido)*
- **SC-202**: Mesma amostra em mg/L e em meq/L produz resultados idênticos. *(atingido —
  verificado: Ep% e somas iguais)*
- **SC-203**: Nenhuma mudança entra em produção sem PR. *(a partir deste PR)*
- **SC-204**: A camada web tem testes verdes no CI/local. *(pendente — FR-207)*

## Assumptions
- Streamlit Community Cloud como plataforma; `main` é a branch de produção.
- A biblioteca `hidrograf` (spec 001) é a fonte única dos cálculos; a UI não os reimplementa.
