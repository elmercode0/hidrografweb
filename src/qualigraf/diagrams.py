"""US5 — Diagramas hidroquímicos: Piper, Stiff, Durov, Schoeller-Berkaloff, Radial (T023).

Cada função recebe um SampleSet e retorna uma matplotlib.figure.Figure.
Usa apenas matplotlib (backend Agg definido pela CLI ao salvar).
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np

from .geometry import _H, ternary_to_xy
from .models import SampleSet, WaterSample

_COLORS = plt.rcParams["axes.prop_cycle"].by_key()["color"]


def _label_points(ax, xs, ys, labels):
    for x, y, lab in zip(xs, ys, labels):
        ax.annotate(str(lab), (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points")


def _draw_triangle(ax, x0=0.0, y0=0.0, scale=1.0):
    pts = [(x0, y0), (x0 + scale, y0), (x0 + scale / 2, y0 + _H * scale), (x0, y0)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color="black", lw=1)


# --- Piper ---------------------------------------------------------------------------

def plot_piper(samples: SampleSet, labels: bool = False, title: str | None = None):
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.set_aspect("equal")
    ax.axis("off")

    gap = 0.25
    # Triângulo de cátions (esquerda): Ca(esq), Na+K(dir), Mg(topo)
    _draw_triangle(ax, 0, 0, 1)
    # Triângulo de ânions (direita): Cl(esq), SO4... na base -> HCO3+CO3(dir), SO4(topo)
    ax_off = 1 + gap
    _draw_triangle(ax, ax_off, 0, 1)
    # Losango central (topo)
    cx = (1 + ax_off) / 2 + 0.0
    dia_y = _H + gap
    d = [(cx, dia_y), (cx + 0.5, dia_y + _H * 0.5),
         (cx, dia_y + _H), (cx - 0.5, dia_y + _H * 0.5), (cx, dia_y)]
    ax.plot([p[0] for p in d], [p[1] for p in d], color="black", lw=1)

    ax.text(0.5, -0.06, "Ca → Na+K", ha="center", fontsize=8)
    ax.text(ax_off + 0.5, -0.06, "Cl → HCO3+CO3", ha="center", fontsize=8)

    cxs, cys, axs, ays, dxs, dys, labs = [], [], [], [], [], [], []
    for i, s in enumerate(samples):
        ca = s.meq("ca") or 0.0
        mg = s.meq("mg") or 0.0
        na = (s.meq("na") or 0.0) + (s.meq("k") or 0.0)
        cl = s.meq("cl") or 0.0
        so4 = s.meq("so4") or 0.0
        hco3 = (s.meq("hco3") or 0.0) + (s.meq("co3") or 0.0)

        if (ca + mg + na) > 0:
            # a=Ca(esq), b=Na+K(dir), c=Mg(topo)
            xc, yc = ternary_to_xy(ca, na, mg)
            cxs.append(xc); cys.append(yc)
        if (cl + so4 + hco3) > 0:
            # a=Cl(esq), b=HCO3+CO3(dir), c=SO4(topo)
            xa, ya = ternary_to_xy(cl, hco3, so4)
            axs.append(ax_off + xa); ays.append(ya)
        # Projeção no losango: usa %Na+K (cátions) e %SO4+Cl (ânions) — projeção padrão
        tot_c = ca + mg + na
        tot_a = cl + so4 + hco3
        if tot_c > 0 and tot_a > 0:
            px = 100 * na / tot_c   # % álcalis
            py = 100 * (so4 + cl) / tot_a  # % ácidos fortes
            # mapeia (px,py) no losango (0..100 -> geometria)
            u = px / 100.0
            v = py / 100.0
            dx = cx + (u - v) * 0.5
            dy = dia_y + (u + v) * _H * 0.5
            dxs.append(dx); dys.append(dy)
        labs.append(s.label)

    ax.scatter(cxs, cys, color=_COLORS[0], s=30, zorder=3)
    ax.scatter(axs, ays, color=_COLORS[1], s=30, zorder=3)
    ax.scatter(dxs, dys, color=_COLORS[2], s=30, zorder=3)
    if labels:
        _label_points(ax, dxs, dys, labs[: len(dxs)])

    ax.set_title(title or "Diagrama de Piper")
    fig.tight_layout()
    return fig


# --- Stiff ---------------------------------------------------------------------------

def plot_stiff(sample: WaterSample, ax=None, title: str | None = None):
    """Diagrama de Stiff para UMA amostra. Cátions à esquerda, ânions à direita."""
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(5, 4))
    else:
        fig = ax.figure

    left = [("Na+K", (sample.meq("na") or 0.0) + (sample.meq("k") or 0.0)),
            ("Ca", sample.meq("ca") or 0.0),
            ("Mg", sample.meq("mg") or 0.0)]
    right = [("Cl", sample.meq("cl") or 0.0),
             ("HCO3+CO3", (sample.meq("hco3") or 0.0) + (sample.meq("co3") or 0.0)),
             ("SO4", sample.meq("so4") or 0.0)]

    ys = [1, 0, -1]
    xs_left = [-v for _, v in left]
    xs_right = [v for _, v in right]
    poly_x = xs_left + xs_right[::-1] + [xs_left[0]]
    poly_y = ys + ys[::-1] + [ys[0]]
    ax.plot(poly_x, poly_y, color=_COLORS[0])
    ax.fill(poly_x, poly_y, alpha=0.3, color=_COLORS[0])
    ax.axvline(0, color="black", lw=0.8)
    for y, (name, _) in zip(ys, left):
        ax.text(min(xs_left) * 1.05 - 0.1, y, name, ha="right", va="center", fontsize=8)
    for y, (name, _) in zip(ys, right):
        ax.text(max(xs_right) * 1.05 + 0.1, y, name, ha="left", va="center", fontsize=8)
    ax.set_yticks([])
    ax.set_xlabel("meq/L")
    ax.set_title(title or f"Stiff — {sample.label}")
    if own:
        fig.tight_layout()
    return fig


def plot_stiff_grid(samples: SampleSet, title: str | None = None):
    """Até 6 diagramas de Stiff simultâneos (como o original)."""
    subset = list(samples)[:6]
    n = len(subset)
    cols = min(3, n) or 1
    rows = math.ceil(n / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3 * rows), squeeze=False)
    for i, s in enumerate(subset):
        plot_stiff(s, ax=axes[i // cols][i % cols])
    for j in range(n, rows * cols):
        axes[j // cols][j % cols].axis("off")
    fig.suptitle(title or "Diagramas de Stiff")
    fig.tight_layout()
    return fig


# --- Durov ---------------------------------------------------------------------------

def plot_durov(samples: SampleSet, labels: bool = False, title: str | None = None):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.axis("off")
    # Quadrado central
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color="black", lw=1)
    ax.text(0.5, -0.06, "Cátions (Ca–Mg–Na+K) →", ha="center", fontsize=8)
    ax.text(-0.06, 0.5, "Ânions (HCO3–SO4–Cl) →", va="center", rotation=90, fontsize=8)

    xs, ys, labs = [], [], []
    for s in samples:
        ca = s.meq("ca") or 0.0
        mg = s.meq("mg") or 0.0
        nak = (s.meq("na") or 0.0) + (s.meq("k") or 0.0)
        hco3 = (s.meq("hco3") or 0.0) + (s.meq("co3") or 0.0)
        so4 = s.meq("so4") or 0.0
        cl = s.meq("cl") or 0.0
        tot_c = ca + mg + nak
        tot_a = hco3 + so4 + cl
        if tot_c <= 0 or tot_a <= 0:
            continue
        # x pela proporção de Na+K entre cátions; y pela proporção de Cl entre ânions
        x = nak / tot_c
        y = cl / tot_a
        xs.append(x); ys.append(y); labs.append(s.label)
    ax.scatter(xs, ys, color=_COLORS[3], s=35, zorder=3)
    if labels:
        _label_points(ax, xs, ys, labs)
    ax.set_title(title or "Diagrama de Durov (modificado / Zaporotec)")
    fig.tight_layout()
    return fig


# --- Schoeller-Berkaloff -------------------------------------------------------------

def plot_schoeller(samples: SampleSet, labels: bool = False, title: str | None = None):
    fig, ax = plt.subplots(figsize=(9, 6))
    ions = ["ca", "mg", "na", "k", "cl", "so4", "hco3"]
    names = ["Ca", "Mg", "Na", "K", "Cl", "SO4", "HCO3"]
    xpos = range(len(ions))
    for i, s in enumerate(samples):
        vals = [s.meq(ion) for ion in ions]
        # substitui zeros/None por um piso pequeno para a escala log
        yv = [(v if (v and v > 0) else 0.01) for v in vals]
        ax.plot(list(xpos), yv, marker="o", label=s.label, color=_COLORS[i % len(_COLORS)])
    ax.set_yscale("log")
    ax.set_xticks(list(xpos))
    ax.set_xticklabels(names)
    ax.set_ylabel("meq/L (log)")
    ax.grid(True, which="both", ls=":", alpha=0.5)
    if labels or len(samples) <= 8:
        ax.legend(fontsize=7)
    ax.set_title(title or "Diagrama de Schoeller-Berkaloff")
    fig.tight_layout()
    return fig


# --- Radial --------------------------------------------------------------------------

def plot_radial(sample: WaterSample, ax=None, title: str | None = None):
    ions = ["ca", "mg", "na", "k", "cl", "so4", "hco3"]
    names = ["Ca", "Mg", "Na", "K", "Cl", "SO4", "HCO3"]
    vals = [sample.meq(ion) or 0.0 for ion in ions]
    angles = np.linspace(0, 2 * np.pi, len(ions), endpoint=False).tolist()
    vals += vals[:1]
    angles += angles[:1]

    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    else:
        fig = ax.figure
    ax.plot(angles, vals, color=_COLORS[0])
    ax.fill(angles, vals, alpha=0.3, color=_COLORS[0])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(names)
    ax.set_title(title or f"Diagrama Radial — {sample.label}")
    if own:
        fig.tight_layout()
    return fig


PLOTTERS = {
    "piper": plot_piper,
    "durov": plot_durov,
    "schoeller": plot_schoeller,
}


def plot(diagram: str, samples: SampleSet, **kw):
    """Dispatcher. Para 'stiff'/'radial' usa grid/primeira amostra."""
    diagram = diagram.lower()
    if diagram in PLOTTERS:
        return PLOTTERS[diagram](samples, **kw)
    if diagram == "stiff":
        return plot_stiff_grid(samples, title=kw.get("title"))
    if diagram == "radial":
        return plot_radial(samples[0], title=kw.get("title"))
    raise ValueError(f"diagrama desconhecido: {diagram}")
