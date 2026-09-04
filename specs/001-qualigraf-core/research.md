# Research & Decisions — QualiGraf-Py

Fontes primárias: `scrapling/page-3-modulos.md` (descrição dos módulos),
`scrapling/assets/Tutorial_QualiGraf.pdf` (tutorial), e literatura hidroquímica padrão
(CETESB, IGAM, CONAMA 357/2005, USSL/Richards 1954, Piper 1944, Stiff 1951, Durov 1948,
Schoeller-Berkaloff).

## 1. Conversão mg/L ↔ meq/L

meq/L = (mg/L × valência) / massa_molar = mg/L / peso_equivalente.

Pesos equivalentes (g/eq) usados como constantes default (overridáveis — o original
permite alterar os "fatores de conversão"):

| Íon | Fórmula | Valência | Peso equiv. (mg/meq) |
|-----|---------|----------|----------------------|
| Ca²⁺ | Ca | 2 | 20.04 |
| Mg²⁺ | Mg | 2 | 12.15 |
| Na⁺ | Na | 1 | 22.99 |
| K⁺ | K | 1 | 39.10 |
| Cl⁻ | Cl | 1 | 35.45 |
| SO₄²⁻ | SO4 | 2 | 48.03 |
| HCO₃⁻ | HCO3 | 1 | 61.02 |
| CO₃²⁻ | CO3 | 2 | 30.00 |
| NO₃⁻ | NO3 | 1 | 62.00 |

**Decisão**: armazenar pesos equivalentes num dict de constantes nomeadas em
`chemistry.py`; `to_meq(mg, ion)` divide pelo peso. Fator = 1/peso_equivalente.

## 2. Balanço Iônico — Erro Prático (Ep%)

**Método dos somatórios** (padrão):

    Ep% = 100 × (ΣCátions − ΣÂnions) / (ΣCátions + ΣÂnions)

com somatórios em meq/L. |Ep%| ≤ ~5–10% indica análise aceitável.

✅ **RESOLVIDO** (fonte: ABQ/CBQ 2009, trabalho 4-59-15, citando Custódio & Llamas 1983 —
a mesma referência que o QualiGraf cita para STD). A fórmula do erro prático é:

    Ep(%) = 100 × (Σânions − Σcátions) / [½ × (Σcátions + Σânions)]     (meq/L)

ou seja, o erro relativo à **média** das somas (equivale ao fator 200 sobre a soma). A
versão que eu usava antes (`100·(ΣC−ΣA)/(ΣC+ΣA)`) dava **metade** do valor — corrigido.

As **"duas técnicas"** do QualiGraf (Tutorial pág. 8) NÃO são duas fórmulas: são a mesma
Ep% comparada a **duas tabelas de tolerância**:

- **Por CE — Custódio & Llamas (1983)**: erro máx. admissível vs. CE (µS/cm):
  50→30% · 200→10% · 500→8% · 2000→4% · >2000→4% (interpolado). `BALANCE_TOLERANCE_CE`.
- **Por soma — Logan (1965)**: erro máx. vs. soma de ânions/cátions (meq/L):
  <1→15% · 1–2→10% · 2–6→6% · 6–10→4% · >10→4%. `BALANCE_TOLERANCE_SUM`.

**Decisão**: `balance` reporta Ep% (uma vez) + `ok_CE` e `ok_Logan`. Removido o antigo
`CE_TO_MEQ_FACTOR` inventado.

## 3. STD (Sólidos Totais Dissolvidos)

    STD (mg/L) = CE (µS/cm) × fator   (fator ∈ [0.55, 0.75], default 0.65)

STD medido em laboratório, se fornecido, prevalece.

**Classificação por STD — tabela do QualiGraf** (Tutorial pág. 12, atribuída à CONAMA
357/2005). ✅ CORRIGIDO conforme a fonte primária (a versão anterior usava 500/30000,
que estava errada):

| Classe | Faixa (STD mg/L) |
|--------|------------------|
| Doce | 0 – 500 |
| Salobra | 500 – 1500 |
| Salgada | 1500 – 35000 |
| Salmoura | > 35000 (ex.: águas marinhas) |

O tutorial também cita a relação de Custódio & Llamas (1983): CE(µS/cm) ≈ 1,35·STD(ppm)
a 18 °C, e adota o fator 0,65 (Santos, 1997) para a estimativa.

**Decisão**: constante `TDS_FACTOR = 0.65`; limiares em `TDS_CLASSES`.

## 4. SAR e Classificação USSL (Richards, 1954)

    SAR = Na / sqrt((Ca + Mg) / 2)      (todos em meq/L)

**Risco de sódio (S)** por SAR:

| Classe | SAR |
|--------|-----|
| S1 (baixo) | < 10 |
| S2 (médio) | 10–18 |
| S3 (alto) | 18–26 |
| S4 (muito alto) | > 26 |

**Risco de salinidade (C)** por CE (µS/cm):

| Classe | CE |
|--------|-----|
| C1 (baixo) | < 250 |
| C2 (médio) | 250–750 |
| C3 (alto) | 750–2250 |
| C4 (muito alto) | > 2250 |

Rótulo USSL = `C{c}S{s}` (ex.: C3S1). O QualiGraf também define **C0** (CE < 100 µS/cm)
— incluída em `USSL_C_THRESHOLDS` (Tutorial pág. 14).

✅ **RESOLVIDO**: os limiares categóricos padrão do USSL (Richards, 1954 — USDA Handbook
60) são de fato os **valores fixos de SAR**: S1 <10 · S2 10–18 · S3 18–26 · S4 >26. As
retas inclinadas do *diagrama* (dependentes da CE) são um refinamento gráfico; a
classificação categórica usa os limiares fixos — que é o que implementamos. Confirmado por
múltiplas fontes que citam Richards (1954).

**Decisão**: limiares em `USSL_C_THRESHOLDS` (com C0) e `USSL_S_THRESHOLDS` (fixos, padrão
Richards 1954).

## 5. IQA — CETESB (produtório ponderado)

    IQA = Π_{i=1}^{9} qi^{wi}

Parâmetros e pesos wi (CETESB):

| # | Parâmetro | wi |
|---|-----------|-----|
| 1 | Oxigênio Dissolvido (% saturação) | 0.17 |
| 2 | Coliformes termotolerantes (NMP/100mL) | 0.15 |
| 3 | pH | 0.12 |
| 4 | DBO₅,₂₀ (mg/L) | 0.10 |
| 5 | Temperatura (variação, °C) | 0.10 |
| 6 | Nitrogênio total (mg/L) | 0.10 |
| 7 | Fósforo total (mg/L) | 0.10 |
| 8 | Turbidez (UNT) | 0.08 |
| 9 | Resíduo total / Sólidos totais (mg/L) | 0.08 |

Σwi = 1.00 (pesos ✅ conferidos com o Tutorial pág. 9–10). Cada qi vem da "curva média
de variação de qualidade" do parâmetro.

✅ **CURVAS DIGITALIZADAS** (antes eram chute): a "Figura 01" (Tutorial pág. 11) foi
renderizada em alta resolução e as 9 curvas lidas ponto a ponto para `iqa_curves.py`. A
própria figura traz um **exemplo resolvido do QualiGraf** (valor observado → qi), usado
como **pontos-âncora de validação** (`ANCHOR_POINTS`):

| parâmetro | observado | qi (QualiGraf) | qi (nossa curva) | ✓ |
|-----------|-----------|----------------|------------------|---|
| OD %sat | 50,15 | 42,43 | 42,16 | ✓ |
| coliformes | 6.000 | 10,95 | 11,00 | ✓ |
| pH | 6,00 | 60,27 | 60,00 | ✓ |
| N total | 1,62 | 87,57 | 87,50 | ✓ |
| P total | 0,25 | 79,07 | 79,00 | ✓ |
| ΔTemperatura | 0 | 94,00 | 94,00 | ✓ |
| turbidez | 90 | 19,71 | 20,00 | ✓ |
| resíduo total | 450 | 39,04 | 39,00 | ✓ |
| **DBO** | **15** | **67,57** | **22,00** | ✗ |

IQA do exemplo: nossas curvas dão **39,15** vs **44** do software — **mesma classe**
(CETESB "Aceitável", IGAM "Ruim"); a diferença vem inteiramente do DBO.

✅ **DBO RESOLVIDO**: a curva desenhada dá q≈22 em DBO=15; a **equação oficial CETESB da
curva de DBO** — `q = 102,6·exp(−0,1101·DBO)` (BasIQA/ABRHidro 2013, reconstruindo CETESB
2005) — dá q≈20. As duas concordam ⇒ o valor **67,57** exibido na tela do QualiGraf (ponto
fora da própria curva) é um **erro de exibição do software**. Mantida a curva (~20–22);
detalhe em `DBO_DISCREPANCY`. Precisão geral da leitura gráfica: ±2–3 q.

📚 As **9 equações analíticas oficiais** (CETESB 2005, forma BasIQA 2013) estão disponíveis
como alternativa de alta fidelidade às curvas digitalizadas — ver tabela abaixo. Mantivemos
os pontos digitalizados por reproduzirem a saída do próprio QualiGraf, mas as equações
servem de validação cruzada.

**Correção de escala**: apenas **coliformes** tem eixo x logarítmico na Figura 01
(`LOG_SCALE_PARAMS = {"coliforms"}`); todos os demais são lineares — a versão anterior
havia log-escalado N/P/sólidos/turbidez por engano.

Se qualquer um dos 9 parâmetros faltar, o IQA é inviabilizado (erro explícito) — conforme
o Tutorial pág. 10.

✅ **OD RESOLVIDO**: o parâmetro é OD em **% de saturação** =
`100 · OD(mg/L) / OD_saturação(T)` (fórmula confirmada pela CETESB). Implementados os
helpers `chemistry.do_saturation_mgl(T, altitude)` (polinômio APHA/Standard Methods,
Elmore & Hayes) e `chemistry.do_saturation_pct(od_mgl, T, altitude)` para converter OD
medido → %sat (o QualiGraf faz isso com o botão "Alterar Altitude"). O campo `do_sat`
recebe a %; use o helper se tiver mg/L.

ℹ️ "Variação de temperatura" (`temp_var`) é o ΔT (afastamento da temperatura de
equilíbrio), pode ser negativo; o alias `temperatura` mapeia para `temp` (bruta), que não
alimenta o IQA por definição do índice.

**Faixas — valores EXATOS lidos da tela do QualiGraf** (corrigidos; a versão anterior
usava 79/51/36/19 e 90/70/50/25):
**CETESB**: Ótimo 80–100 · Bom 52–80 · Aceitável 37–52 · Ruim 20–37 · Péssima 0–20.
**IGAM/MG**: Excelente 90–100 · Bom 70–90 · Médio 50–70 · Ruim 25–50 · Muito Ruim 0–25.

**Decisão**: pesos em `IQA_WEIGHTS`; curvas qi digitalizadas da Figura 01 em
`iqa_curves.py` (interpolação linear, exceto coliformes em log10); duas tabelas de faixas
(`IQA_RANGES_CETESB`, `IQA_RANGES_IGAM`) com os limiares exatos do software.

**Equações analíticas oficiais (CETESB 2005 / BasIQA 2013)** — validação cruzada:

| Parâmetro | Equação (q) | Coeficientes |
|-----------|-------------|--------------|
| OD %sat | A·exp((%O₂+B)²/C) | A=100,8 B=−106 C=−3745 |
| Coliformes | A+B·log₁₀CF+C·log₁₀CF²+D·log₁₀CF³ | A=98,03 B=−36,45 C=3,138 D=0,06776 (>10⁵→3) |
| pH | forma A·pH^(B·pH+C·pH²)+5,213 | A=0,05421 B=1,23 C=−0,09873 (pH<2→2; >12→3) |
| DBO | A·exp(B·DBO) | A=102,6 B=−0,1101 (>30→2) |
| N total | A·NT^(B+C·NT) | A=98,96 B=−0,2232 C=−0,006457 (>100→1) |
| Fósforo | A·exp(B·FT+C) | A=213,7 B=−1,680 C=0,3325 (>10→1) |
| Turbidez | A·exp(B·TU+C·√TU) | A=97,34 B=−0,01139 C=−0,04917 |
| ΔTemperatura | 1/(A·ΔT²+B+C) | A=0,0003869 B=0,1815 C=0,01081 (ΔT>15→9) |
| Resíduo total | A·exp(B·ST+C·√ST+D·ST) | A=80,26 B=−0,00107 C=0,03009 D=−0,1185 |

(Alguns coeficientes vêm de OCR do PDF; conferir sinais/potências antes de adotar como
implementação primária. Coincidem com as curvas digitalizadas dentro de ±3 q.)

## 6. Diagramas

- **Piper**: dois triângulos (cátions: Ca–Mg–Na+K; ânions: Cl–SO4–HCO3+CO3, em % meq) +
  losango central; projeção padrão de coordenadas triangulares → cartesianas.
- **Stiff**: polígono com cátions à esquerda e ânions à direita em eixos horizontais
  (meq/L); Na+K, Ca, Mg (esq.) vs Cl, HCO3+CO3, SO4 (dir.).
- **Durov/Zaporotec**: dois triângulos ternários projetados sobre um quadrado central,
  com pH e STD em painéis adjacentes.
- **Schoeller-Berkaloff**: eixo Y logarítmico (meq/L) com colunas por íon, uma linha por
  amostra.
- **Radial**: polígono radial (um raio por íon em meq/L).

**Decisão**: `matplotlib` puro (sem libs de nicho) para portabilidade; cada diagrama é
uma função `plot_*(sampleset, ax=None, **opts) -> Figure`. Coordenadas triangulares
implementadas em `geometry.py` e testadas com vértices conhecidos.

## 7. Estatísticas e Correlação

- Estatísticas: n, min, max, média, variância (amostral, ddof=1), desvio-padrão — via
  numpy/pandas.
- Correlação: ajuste linear (e opcionalmente potência/exponencial/log) por mínimos
  quadrados; R² = 1 − SS_res/SS_tot.

**Decisão**: `numpy.polyfit`/`lstsq`; R² calculado explicitamente.

## 8. Alternativas consideradas

| Decisão | Alternativa rejeitada | Motivo |
|---------|-----------------------|--------|
| matplotlib | plotly/bokeh | evita dependência pesada; PNG/SVG offline; suficiente |
| typer | argparse puro | menos boilerplate, ajuda e `--json` fáceis; já no ambiente |
| interpolação linear das curvas IQA | reimplementar polinômios oficiais | fontes dos polinômios variam; interpolação dos pontos é transparente e testável |
| src/ layout | flat | isola pacote, evita import acidental em testes |
