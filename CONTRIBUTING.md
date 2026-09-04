# Contribuindo — Hidrograf

Este projeto segue **desenvolvimento spec-driven** (spec-kit) com **gate de produção por
PR**. Regras da constituição (`.specify/memory/constitution.md`, Princípio VI).

## Fluxo de uma mudança

1. **Spec primeiro.** Nova feature começa por spec/plan/tasks:
   - `specify` (ou editar `specs/NNN-<slug>/spec.md`) → `plan.md` → `tasks.md`.
   - Correções pequenas/bugfix: pelo menos referencie a spec/task afetada no commit.
2. **Branch de feature.** Nunca trabalhe direto na `main`:
   ```bash
   git checkout -b spec/NNN-<slug>      # ou fix/<slug>, chore/<slug>
   ```
3. **Implemente + teste.** `pytest` verde e `ruff` limpo:
   ```bash
   pytest -q && ruff check src tests streamlit_app.py
   ```
   Mudança de UI: verifique o boot do app (`streamlit run streamlit_app.py`).
4. **Abra um PR** para a `main`:
   ```bash
   git push -u origin <branch>
   gh pr create --fill --base main
   ```
5. **Merge = deploy.** Ao aprovar e mergear na `main`, o Streamlit Cloud redeploya
   automaticamente. **Nada entra em produção sem PR.**

## Produção

- **`main` é a branch de produção** (Streamlit Cloud publica a partir dela).
- Recomendado: ativar *branch protection* na `main` no GitHub exigindo PR (task T216).

## Gates de qualidade (obrigatórios no PR)

- `pytest` verde (inclui testes de valor-fixado dos cálculos).
- `ruff check` limpo.
- Mudança científica → atualizar `research.md` com a fonte/citação.
- Constante nova → nomeada e documentada (Princípio IV).

## Reconciliação

Se algo foi construído fora do fluxo, documente-o com uma spec de reconciliação
(ver `specs/002-web-delivery/`) e registre as tasks já feitas como `[x]` e as pendências
como `[ ]`.
