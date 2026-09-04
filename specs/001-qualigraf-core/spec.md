# Feature Specification: QualiGraf-Py — Núcleo de Análise Hidroquímica

**Feature Branch**: `001-qualigraf-core`

**Created**: 2026-09-04

**Status**: Draft

**Input**: Reimplementar em Python, como biblioteca + CLI, os módulos de análise
hidroquímica descritos na página "Módulos" do QualiGraf da FUNCEME
(`scrapling/page-3-modulos.md`), usando os detalhes do dump em `scrapling/`
(inclusive o tutorial em `scrapling/assets/Tutorial_QualiGraf.pdf`).

## Contexto

O **QualiGraf** (FUNCEME, desktop Windows, VB) auxilia a análise gráfica de qualidade
de amostras de água. Esta feature entrega um equivalente moderno, multiplataforma e
programável em Python: uma biblioteca de cálculos puros + uma CLI, capaz de ler uma
planilha de amostras e produzir tabelas, classificações e diagramas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Balanço Iônico (Priority: P1) 🎯 MVP

Um hidrogeólogo carrega uma planilha de amostras (cátions e ânions em mg/L) e obtém,
por amostra, as concentrações em meq/L e o erro prático do balanço iônico (Ep%), para
validar a qualidade da análise laboratorial.

**Why this priority**: É a verificação fundamental de consistência de qualquer análise
hidroquímica; sem ela as demais análises não são confiáveis. Sozinha já entrega valor.

**Independent Test**: Rodar `qualigraf balance amostras.csv` e conferir Ep% contra um
caso calculado à mão.

**Acceptance Scenarios**:

1. **Given** amostra com Ca, Mg, Na, K, Cl, SO4, HCO3, CO3 em mg/L, **When** calculo o
   balanço iônico, **Then** recebo cada íon em meq/L, ΣCátions, ΣÂnions e Ep% pelo método
   dos somatórios.
2. **Given** a amostra também tem Condutividade Elétrica (CE), **When** solicito o método
   por CE, **Then** recebo o Ep% pela técnica baseada em CE.
3. **Given** coeficientes de conversão mg/L→meq/L customizados, **When** os informo,
   **Then** os cálculos usam meus coeficientes.

---

### User Story 2 - Sólidos Totais Dissolvidos + Classificação CONAMA (Priority: P1)

O usuário estima STD a partir da CE (fator 0,65) ou informa o STD de laboratório e
classifica as águas em Doces/Salobras/Salgadas conforme a Resolução CONAMA 357/2005.

**Why this priority**: Cálculo simples, de alto uso, e base para outras análises
(Durov usa STD). MVP independente.

**Independent Test**: `qualigraf tds amostras.csv` e conferir classe por faixa de STD.

**Acceptance Scenarios**:

1. **Given** CE em µS/cm, **When** calculo STD, **Then** STD = CE × fator (default 0,65) e
   recebo a classe CONAMA.
2. **Given** STD medido em laboratório, **When** o informo, **Then** ele prevalece sobre a
   estimativa por CE.

---

### User Story 3 - Classificação para Irrigação SAR/USSL (Priority: P2)

O usuário calcula a Razão de Adsorção de Sódio (SAR) e obtém a classe USSL de cada
amostra (combinação risco de salinidade C1–C4 × risco de sódio S1–S4).

**Why this priority**: Uso agronômico central do QualiGraf; depende de meq/L (US1).

**Independent Test**: `qualigraf sar amostras.csv` conferindo SAR e rótulo (ex.: C3S1).

**Acceptance Scenarios**:

1. **Given** Na, Ca, Mg em meq/L, **When** calculo SAR, **Then** SAR = Na/√((Ca+Mg)/2).
2. **Given** SAR e CE, **When** classifico, **Then** recebo a classe USSL (Cx Sy).

---

### User Story 4 - Índice de Qualidade da Água (IQA) (Priority: P2)

O usuário calcula o IQA (0–100) pelo produtório ponderado CETESB de 9 parâmetros e
recebe a classificação nas faixas CETESB e IGAM.

**Why this priority**: Índice muito solicitado; mais complexo (curvas qi). Independente
das demais.

**Independent Test**: `qualigraf iqa amostras.csv` conferindo IQA contra caso de
referência; erro claro se faltar algum dos 9 parâmetros.

**Acceptance Scenarios**:

1. **Given** os 9 parâmetros (OD, coliformes termotolerantes, pH, DBO, variação de
   temperatura, N total, P total, turbidez, resíduo total), **When** calculo o IQA,
   **Then** IQA = Π qi^wi e recebo as classes CETESB e IGAM.
2. **Given** falta um dos 9 parâmetros, **When** calculo, **Then** recebo erro explícito
   nomeando o parâmetro ausente.

---

### User Story 5 - Diagramas Hidroquímicos (Priority: P2)

O usuário gera os diagramas clássicos a partir da planilha: **Piper**, **Stiff**,
**Durov (Zaporotec)**, **Schoeller-Berkaloff** (escala log) e **Radial**, salvos como
arquivos de imagem, com opção de rotular/selecionar amostras.

**Why this priority**: É a razão de ser gráfica do QualiGraf. Depende de meq/L (US1).

**Independent Test**: `qualigraf plot piper amostras.csv -o piper.png` gera a imagem e
posiciona os pontos corretamente para uma amostra conhecida.

**Acceptance Scenarios**:

1. **Given** amostras com os íons principais, **When** gero o Piper, **Then** um PNG é
   criado com os triângulos de cátions/ânions e o losango central.
2. **Given** uma amostra, **When** gero um Stiff, **Then** o polígono usa meq/L nos eixos.
3. **Given** várias amostras, **When** gero Schoeller, **Then** as linhas usam escala
   logarítmica.

---

### User Story 6 - Estatísticas e Correlação (Priority: P3)

O usuário obtém estatísticas básicas por parâmetro (n, mín, máx, média, variância,
desvio-padrão) e ajusta correlações entre íons por mínimos quadrados, com R².

**Why this priority**: Inspeção exploratória; complementar. Independente.

**Independent Test**: `qualigraf stats amostras.csv` e `qualigraf correlate amostras.csv
--x Cl --y Na` conferindo média/R² à mão.

**Acceptance Scenarios**:

1. **Given** uma planilha, **When** peço estatísticas, **Then** recebo n, mín, máx, média,
   variância e desvio-padrão por coluna numérica.
2. **Given** dois íons, **When** ajusto correlação, **Then** recebo coeficientes e R².

### Edge Cases

- Coluna ausente para uma análise → erro nomeando a coluna e a análise afetada.
- Valores não numéricos / vazios em uma amostra → amostra reportada como inválida, não
  descartada em silêncio.
- Divisão por zero em SAR ((Ca+Mg)=0) → resultado marcado como indefinido, não crash.
- Arquivo inexistente ou formato não suportado → erro claro em stderr, exit code ≠ 0.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE ler amostras de arquivos CSV e XLSX com colunas nomeadas
  (íons e parâmetros), mapeáveis por aliases (ex.: `Na`, `Sodio`, `Na+`).
- **FR-002**: O sistema DEVE converter concentrações mg/L → meq/L usando pesos
  equivalentes por íon, com coeficientes overridáveis.
- **FR-003**: O sistema DEVE calcular o balanço iônico: meq/L por íon, ΣCátions,
  ΣÂnions e Ep% pelos métodos (a) somatórios e (b) condutividade elétrica.
- **FR-004**: O sistema DEVE estimar STD = CE × fator (default 0,65, configurável) ou
  aceitar STD medido, e classificar por CONAMA 357/2005 (Doce/Salobra/Salgada).
- **FR-005**: O sistema DEVE calcular SAR = Na/√((Ca+Mg)/2) e a classe USSL (C1–C4 × S1–S4).
- **FR-006**: O sistema DEVE calcular o IQA (produtório ponderado de 9 parâmetros, pesos
  CETESB) e classificar nas faixas CETESB e IGAM; DEVE falhar explicitamente se faltar
  qualquer um dos 9 parâmetros.
- **FR-007**: O sistema DEVE gerar diagramas de Piper, Stiff, Durov, Schoeller-Berkaloff
  e Radial como arquivos de imagem.
- **FR-008**: O sistema DEVE calcular estatísticas básicas (n, mín, máx, média, variância,
  desvio-padrão) por parâmetro.
- **FR-009**: O sistema DEVE ajustar correlações entre dois parâmetros por mínimos
  quadrados e reportar R² (aderência do modelo).
- **FR-010**: Toda análise DEVE ser exposta na CLI com saída humana (tabela) e `--json`.
- **FR-011**: O sistema DEVE poder exportar resultados tabulares para .txt/.csv (como o
  original permite gravar em arquivo).
- **FR-012**: Toda constante científica (pesos equivalentes, fator STD, pesos IQA,
  limiares de classes) DEVE ser um valor nomeado documentado com sua fonte.
- **FR-013**: O sistema DEVE tratar unidades de entrada de forma explícita: íons em mg/L,
  CE em µS/cm. DEVE rejeitar/avisar quando um valor esperado numérico não for numérico
  (não descartar amostra em silêncio — Princípio V). [Conversão automática de dS/m/mS/cm →
  fora do escopo v1; documentar exigência de µS/cm.]
- **FR-014**: Análises cujas fórmulas/curvas NÃO puderam ser validadas contra a fonte
  (IQA e Ep% por CE) DEVEM ser marcadas como PROVISÓRIAS e emitir aviso ao usuário.
- **FR-015**: O balanço iônico DEVE sinalizar quando faltar algum íon maior
  (Ca, Mg, Na, Cl, SO₄, HCO₃), pois o Ep% fica pouco confiável.

### Key Entities *(include if feature involves data)*

- **WaterSample**: uma amostra — id/rótulo, concentrações de íons (mg/L e/ou meq/L),
  parâmetros físico-químicos (CE, pH, temperatura, OD, DBO, turbidez, coliformes, N, P,
  STD), coordenadas opcionais (lat/long) para uso em mapa.
- **SampleSet**: coleção de WaterSample carregada de um arquivo; expõe acesso tabular.
- **BalanceResult / TDSResult / SARResult / IQAResult / StatsResult / CorrelationResult**:
  estruturas de resultado por análise, serializáveis para JSON.
- **Diagram**: especificação de um diagrama (tipo, amostras selecionadas, opções de
  rótulo/cor) que produz um arquivo de imagem.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Para uma amostra de referência, o Ep% calculado difere do valor conferido à
  mão em menos de 0,1 ponto percentual.
- **SC-002**: A classe CONAMA, a classe USSL e as faixas IQA/CETESB/IGAM de casos de
  referência batem 100% com a classificação esperada.
- **SC-003**: `qualigraf plot piper|stiff|durov|schoeller|radial` produz um arquivo de
  imagem não vazio para uma planilha de exemplo, em < 5 s por diagrama.
- **SC-004**: Um novo usuário processa uma planilha de exemplo do início ao fim seguindo
  o `quickstart.md` sem editar código.
- **SC-005**: 100% dos módulos de cálculo possuem teste de valor-fixado verde.

## Assumptions

- Concentrações de entrada em mg/L, CE em µS/cm. **Não há conversão automática de unidade
  em v1**; fornecer CE em dS/m ou mS/cm produziria STD/USSL 1000× errados — exigência de
  µS/cm documentada no quickstart/README.
- Escopo v1: análises, classificações, tabelas e diagramas estáticos (PNG/SVG). Fora do
  escopo v1: GUI desktop, acesso a Google Maps, integração com editores/planilhas e
  impressão direta (itens "Miscelânea" do original).
- Reproduzimos os cálculos e a semântica dos módulos, não o layout visual pixel-a-pixel
  dos gráficos do software original.

## Pendências de validação — RESOLVIDAS

Fontes: `scrapling/` (dump), Figura 01 do `Tutorial_QualiGraf.pdf` (digitalizada), e
literatura autoritativa (CETESB/Apêndice E, ABQ/CBQ 2009, BasIQA/ABRHidro 2013, Custódio &
Llamas 1983, Logan 1965, Richards 1954/USDA Handbook 60, APHA). Ver `research.md` para
citações e fórmulas.

| Item | Status | Fonte / resolução |
|------|--------|-------------------|
| Limiares STD/CONAMA | ✅ | Tabela do Tutorial (Doce/Salobra/Salgada/Salmoura) |
| Classe C0 do USSL | ✅ | Tutorial pág. 14 |
| Faixas IQA CETESB/IGAM | ✅ | Valores exatos da tela (80/52/37/20 e 90/70/50/25) |
| Curvas qi do IQA | ✅ | Digitalizadas da Figura 01; 8/9 âncoras conferem |
| Escala das curvas | ✅ | Só coliformes é log; demais lineares (Figura 01) |
| ΔTemperatura negativo | ✅ | Curva cobre −5…+20 °C |
| **DBO (curva vs exemplo)** | ✅ RESOLVIDO | Eq. CETESB `q=102,6·exp(−0,1101·DBO)` dá ≈20 = curva; 67,57 da tela é **bug do QualiGraf** (BasIQA 2013) |
| **Ep% (fórmula)** | ✅ RESOLVIDO | Custódio & Llamas 1983: `100·(Σan−Σcat)/(½(Σcat+Σan))` — antes estava pela metade |
| **"Duas técnicas" do Ep%** | ✅ RESOLVIDO | Mesma Ep%, 2 tolerâncias: CE (Custódio & Llamas) e soma (Logan 1965); tabelas implementadas |
| **Classes de sódio S1–S4 (USSL)** | ✅ RESOLVIDO | Limiares fixos 10/18/26 são o padrão categórico (Richards 1954) |
| **OD em % de saturação** | ✅ RESOLVIDO | `100·OD/OD_sat(T)`; helpers `do_saturation_*` (APHA) |
| **Dataset de referência** | ✅ (parcial) | Exemplo da Figura 01 validado (8/9). O `.exe` é VB6 compilado/UPX — não roda headless |

⚠️ **Notas remanescentes** (baixo risco): (a) alguns coeficientes das equações CETESB vêm
de OCR — conferir antes de trocar as curvas digitalizadas pelas analíticas; (b) validação
ampla exigiria rodar o QualiGraf (Windows) com mais amostras — as curvas digitalizadas +
equações CETESB tornam isso opcional.
