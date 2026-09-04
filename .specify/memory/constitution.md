# Hidrograf Constitution

## Core Principles

### I. Library-First, Domain-Pure
Every hydrochemistry capability is implemented first as a pure, standalone function
or class in the `hidrograf` library, free of I/O and UI concerns. Calculations
(ionic balance, IQA, TDS, SAR, diagrams data) take plain numeric inputs and return
plain data structures. No calculation module may import the CLI, read files, or print.
This guarantees each analysis is independently testable and embeddable.

### II. CLI Interface
Every user-facing capability is reachable through the `hidrograf` CLI. The CLI follows
a text in/out protocol: file/args in → results to stdout, errors to stderr. Every
command supports both a human-readable table view and a `--json` machine-readable
output. Plotting commands write image files and print their paths.

### III. Test-First for Numerics (NON-NEGOTIABLE)
Every calculation module ships with unit tests that pin its output against known
reference values (hand-computed or from the QualiGraf documentation). Numeric results
are asserted with explicit tolerances. A calculation without a value-pinning test is
considered incomplete.

### IV. Scientific Traceability
Every formula, coefficient, weight, and classification threshold cites its source in a
docstring or comment (CETESB, IGAM, CONAMA 357/2005, USSL, Piper, Stiff, Durov,
Schoeller-Berkaloff). Default coefficients (e.g. TDS factor 0.65, mg/L↔meq/L
equivalent weights) are named constants, not magic numbers, and are overridable.

### V. Graceful, Explicit Data Handling
Water-sample inputs are frequently incomplete. Modules validate required parameters and
fail with a clear, specific error naming the missing/invalid field (e.g. IQA requires
all 9 parameters). Unit conversions are explicit. Charts and tables never silently drop
samples — dropped/invalid samples are reported.

## Technology Constraints

- Language: Python ≥ 3.11.
- Core numeric stack: `numpy`, `pandas` for tabular I/O, `matplotlib` for diagrams.
- CLI: `typer`. Packaging: `pyproject.toml` (PEP 621), `src/` layout.
- The library core requires no network at runtime (offline-capable, like the original).
- **Web delivery (added v1.1.0):** a thin Streamlit UI (`streamlit_app.py`) is a supported
  delivery target, deployed on Streamlit Community Cloud. It MUST only import `hidrograf`
  and contain no calculation logic (Principle I). Earlier "GUI/web out of scope" is
  superseded; see `specs/002-web-delivery/`.
- Inputs: CSV/XLSX of water samples; ion concentrations in mg/L **or** meq/L (unit
  detected from the header or supplied by the user), CE in µS/cm.

## Development Workflow

- Each module maps to a user story in `spec.md`; work proceeds story-by-story, each an
  independently shippable MVP increment.
- `pytest` gate: all value-pinning tests green before a story is marked done.
- Formatting/linting via `ruff`; type hints on all public functions.

### VI. Spec-First Delivery (added v1.1.0)

- Every new feature starts with spec → plan → tasks BEFORE code. Reverse-documenting
  (`converge`) is a remediation, not the norm.
- **Nothing reaches production without a PR.** `main` is the production branch (auto-deploys
  to Streamlit Cloud); changes land only via feature branch → PR → merge. No direct pushes.
- Quality gate on every PR: `pytest` green + `ruff` clean; user-facing changes exercised
  (app boots / flow driven) before merge.

## Governance

This constitution guides all spec, plan, task, and implementation decisions for
Hidrograf. Any deviation (extra dependency, skipped test, magic constant, out-of-flow
change) must be justified in the plan's Complexity Tracking table. Simplicity and
scientific fidelity win ties.

**Version**: 1.1.0 | **Ratified**: 2026-09-04 | **Last Amended**: 2026-09-04
<!-- v1.1.0: web/UI moved into scope; added Principle VI (spec-first delivery + PR gate). -->

