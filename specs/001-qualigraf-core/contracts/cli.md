# CLI Contract — `qualigraf`

Convenção geral: `qualigraf <comando> <ARQUIVO> [opções]`. Toda saída tabular aceita
`--json` (machine-readable em stdout). Erros → stderr, exit code ≠ 0. `--output/-o` grava
resultado em arquivo (.txt/.csv para tabelas; .png/.svg para diagramas).

| Comando | Descrição | Args/Opções chave | Saída |
|---------|-----------|-------------------|-------|
| `balance` | Balanço iônico (US1) | `FILE` · `--method sum\|ec\|both` · `--json` | meq/íon, ΣCát, ΣÂn, Ep% |
| `tds` | STD + CONAMA (US2) | `FILE` · `--factor 0.65` · `--json` | STD, fonte, classe |
| `sar` | SAR + USSL (US3) | `FILE` · `--json` | SAR, C, S, rótulo USSL |
| `iqa` | IQA CETESB+IGAM (US4) | `FILE` · `--json` | IQA, qi, classes |
| `stats` | Estatísticas básicas (US6) | `FILE` · `--columns ...` · `--json` | n/min/max/média/var/dp |
| `correlate` | Correlação + R² (US6) | `FILE` · `--x` · `--y` · `--model linear\|power\|log\|exp` · `--json` | coeffs, R² |
| `plot` | Diagramas (US5) | `plot {piper\|stiff\|durov\|schoeller\|radial} FILE -o out.png` · `--labels` · `--select L1,L2` | arquivo de imagem |
| `convert` | mg/L ↔ meq/L de uma planilha | `FILE` · `--to meq\|mg` · `-o` | planilha convertida |

Exemplos:

```bash
qualigraf balance tests/data/sample_waters.csv --method both
qualigraf tds amostras.csv --factor 0.7 --json
qualigraf sar amostras.csv -o sar.csv
qualigraf iqa amostras.csv --json
qualigraf plot piper amostras.csv -o piper.png --labels
qualigraf correlate amostras.csv --x Cl --y Na --model linear
```

Contrato de erro (exemplos):
- arquivo inexistente → `erro: arquivo não encontrado: <path>` (exit 2)
- coluna faltando p/ análise → `erro: análise 'sar' requer coluna 'Na' (ausente)` (exit 3)
- IQA com parâmetro ausente → `erro: IQA requer 'do_sat' (ausente na amostra L3)` (exit 3)
