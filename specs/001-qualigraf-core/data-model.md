# Data Model — QualiGraf-Py

## WaterSample
Uma amostra de água. Todos os campos de concentração opcionais (dados são incompletos).

| Campo | Tipo | Unid. | Notas |
|-------|------|-------|-------|
| label | str | — | id/rótulo da amostra |
| ca, mg, na, k | float? | mg/L | cátions principais |
| cl, so4, hco3, co3, no3 | float? | mg/L | ânions principais |
| ec | float? | µS/cm | Condutividade Elétrica |
| ph | float? | — | |
| tds | float? | mg/L | STD medido (opcional) |
| temp, temp_var | float? | °C | temperatura / variação p/ IQA |
| do_sat | float? | % | Oxigênio Dissolvido (saturação) p/ IQA |
| bod | float? | mg/L | DBO p/ IQA |
| coliforms | float? | NMP/100mL | coliformes termotolerantes p/ IQA |
| n_total, p_total | float? | mg/L | p/ IQA |
| turbidity | float? | UNT | p/ IQA |
| total_solids | float? | mg/L | resíduo total p/ IQA |
| lat, lon | float? | ° | coordenadas opcionais |

Métodos: `meq(ion) -> float` (converte via `chemistry`), `has(*fields) -> bool`.

## SampleSet
Coleção de `WaterSample`, tipicamente de um arquivo.
- `from_file(path)` (io) · `to_dataframe()` · iterável · `select(labels)`.

## Result types (dataclasses, todos com `to_dict()` p/ JSON)

- **BalanceResult**: label, meq por íon, sum_cations, sum_anions, ep_sum (%), ep_ec (%|None), acceptable(bool).
- **TDSResult**: label, tds (mg/L), source ("measured"|"estimated"), ec, factor, conama_class.
- **SARResult**: label, sar (float|None), ec, c_class (C1..C4), s_class (S1..S4), ussl_label.
- **IQAResult**: label, iqa (float), qi (dict param→qi), cetesb_class, igam_class; erro se faltar parâmetro.
- **StatsResult**: por parâmetro → n, min, max, mean, variance, std.
- **CorrelationResult**: x, y, model, coeffs, r2, n.

## Diagram specs
`DiagramType ∈ {piper, stiff, durov, schoeller, radial}`; opções: labels(bool),
selected(labels|None), title, cores. Saída: arquivo de imagem (PNG/SVG).

## Constants (constants.py) — ver research.md p/ valores e fontes
`EQUIVALENT_WEIGHTS`, `CE_TO_MEQ_FACTOR`, `TDS_FACTOR`, `TDS_CLASSES`,
`USSL_C_THRESHOLDS`, `USSL_S_THRESHOLDS`, `IQA_WEIGHTS`, `IQA_RANGES_CETESB`,
`IQA_RANGES_IGAM`, `COLUMN_ALIASES`.
