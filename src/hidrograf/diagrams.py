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

# Layout clássico (base do triângulo = 1): cátions em x=0..1, ânions em x=2..3 e losango
# centrado em cima do vão, com vértice inferior na altura do topo dos triângulos.
_GAP = 1.0
_ANION_X0 = 1.0 + _GAP
_DIA_CX = (1.0 + _ANION_X0) / 2.0
_DIA_CY = (1.0 + _GAP) * _H

_GRID_KW = {"color": "0.78", "lw": 0.6, "zorder": 1}
_EDGE_KW = {"color": "black", "lw": 1.8, "zorder": 4, "solid_joinstyle": "miter"}

# Rótulos com mathtext em negrito, iguais aos usados na literatura.
_L_CA = r"$\mathbf{Ca^{2+}}$"
_L_MG = r"$\mathbf{Mg^{2+}}$"
_L_NAK = r"$\mathbf{Na^{+}{+}K^{+}}$"
_L_CL = r"$\mathbf{Cl^{-}}$"
_L_SO4 = r"$\mathbf{SO_4^{2-}}$"
_L_HCO3 = r"$\mathbf{HCO_3^{-}{+}CO_3^{2-}}$"
_L_CAMG = r"$\mathbf{Ca^{2+}{+}Mg^{2+}}$"
_L_SO4CL = r"$\mathbf{SO_4^{2-}{+}Cl^{-}}$"


def _sample_colors(n: int) -> list:
    """Uma cor por amostra (tab10 até 10 amostras, tab20 acima disso)."""
    cmap = plt.get_cmap("tab10" if n <= 10 else "tab20")
    k = 10 if n <= 10 else 20
    return [cmap(i % k) for i in range(n)]


def _tri_vertices(x0: float) -> tuple[tuple[float, float], ...]:
    """(esquerdo, direito, topo) do triângulo equilátero com base [x0, x0+1]."""
    return (x0, 0.0), (x0 + 1.0, 0.0), (x0 + 0.5, _H)


def _tri_grid(ax, x0: float, steps: int = 10) -> None:
    """Malha ternária a cada 10% — as três famílias de linhas paralelas aos lados."""
    a, b, c = _tri_vertices(x0)
    for i in range(1, steps):
        f = i / steps
        for p, q in (
            ((a[0] + f * (c[0] - a[0]), a[1] + f * (c[1] - a[1])),
             (b[0] + f * (c[0] - b[0]), b[1] + f * (c[1] - b[1]))),
            ((a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])),
             (a[0] + f * (c[0] - a[0]), a[1] + f * (c[1] - a[1]))),
            ((b[0] + f * (a[0] - b[0]), b[1] + f * (a[1] - b[1])),
             (b[0] + f * (c[0] - b[0]), b[1] + f * (c[1] - b[1]))),
        ):
            ax.plot([p[0], q[0]], [p[1], q[1]], **_GRID_KW)
    ax.plot([a[0], b[0], c[0], a[0]], [a[1], b[1], c[1], a[1]], **_EDGE_KW)


def _diamond_xy(u: float, v: float) -> tuple[float, float]:
    """Ponto do losango a partir de u=%(Na+K) dos cátions e v=%(SO4+Cl) dos ânions.

    Equivale à projeção clássica: sobe-se do ponto dos cátions a 60° e do ponto dos
    ânions a 120° até a interseção.
    """
    return _DIA_CX + 0.5 * (u + v - 1.0), _DIA_CY + _H * (v - u)


def _diamond_grid(ax, steps: int = 10) -> None:
    for i in range(1, steps):
        f = i / steps
        for p, q in ((_diamond_xy(f, 0.0), _diamond_xy(f, 1.0)),
                     (_diamond_xy(0.0, f), _diamond_xy(1.0, f))):
            ax.plot([p[0], q[0]], [p[1], q[1]], **_GRID_KW)
    corners = [_diamond_xy(0, 0), _diamond_xy(1, 0), _diamond_xy(1, 1), _diamond_xy(0, 1)]
    corners.append(corners[0])
    ax.plot([p[0] for p in corners], [p[1] for p in corners], **_EDGE_KW)


def plot_piper(samples: SampleSet, labels: bool = False, title: str | None = None):
    """Diagrama de Piper: triângulo de cátions, de ânions e losango de projeção.

    Cátions: Ca (esq.), Na+K (dir.), Mg (topo). Ânions: HCO3+CO3 (esq.), Cl (dir.),
    SO4 (topo). Cada amostra recebe uma cor única nos três painéis, ligada por linhas
    de projeção pontilhadas.
    """
    fig, ax = plt.subplots(figsize=(10.5, 9.5))
    ax.set_aspect("equal")
    ax.axis("off")

    _tri_grid(ax, 0.0)
    _tri_grid(ax, _ANION_X0)
    _diamond_grid(ax)

    tk = {"fontsize": 13, "zorder": 6}
    # Triângulo dos cátions
    ax.text(-0.03, -0.075, _L_CA, ha="center", va="top", **tk)
    ax.text(1.03, -0.075, _L_NAK, ha="center", va="top", **tk)
    ax.text(0.5, _H + 0.05, _L_MG, ha="center", va="bottom", **tk)
    # Triângulo dos ânions
    ax.text(_ANION_X0 + 0.02, -0.075, _L_HCO3, ha="center", va="top", **tk)
    ax.text(_ANION_X0 + 1.03, -0.075, _L_CL, ha="center", va="top", **tk)
    ax.text(_ANION_X0 + 0.5, _H + 0.05, _L_SO4, ha="center", va="bottom", **tk)
    # Losango
    ax.text(_DIA_CX, _DIA_CY + _H + 0.06, _L_SO4CL, ha="center", va="bottom", **tk)
    ax.text(_DIA_CX, _DIA_CY - _H - 0.08, _L_NAK, ha="center", va="top", **tk)
    off = 0.14  # afastamento perpendicular aos lados superiores do losango
    ax.text(_DIA_CX - 0.25 - off * _H, _DIA_CY + _H / 2 + off * 0.5, _L_CAMG,
            ha="center", va="center", rotation=60, **tk)
    ax.text(_DIA_CX + 0.25 + off * _H, _DIA_CY + _H / 2 + off * 0.5, _L_HCO3,
            ha="center", va="center", rotation=-60, **tk)

    colors = _sample_colors(len(samples))
    handles, plotted = [], []
    for i, s in enumerate(samples):
        ca = s.meq("ca") or 0.0
        mg = s.meq("mg") or 0.0
        nak = (s.meq("na") or 0.0) + (s.meq("k") or 0.0)
        cl = s.meq("cl") or 0.0
        so4 = s.meq("so4") or 0.0
        hco3 = (s.meq("hco3") or 0.0) + (s.meq("co3") or 0.0)
        tot_c, tot_a = ca + mg + nak, cl + so4 + hco3
        color = colors[i]

        pts = []
        if tot_c > 0:
            # a=Ca (esq.), b=Na+K (dir.), c=Mg (topo)
            pts.append(ternary_to_xy(ca, nak, mg))
        if tot_a > 0:
            # a=HCO3+CO3 (esq.), b=Cl (dir.), c=SO4 (topo)
            xa, ya = ternary_to_xy(hco3, cl, so4)
            pts.append((_ANION_X0 + xa, ya))
        if tot_c > 0 and tot_a > 0:
            dp = _diamond_xy(nak / tot_c, (so4 + cl) / tot_a)
            for p in pts:  # linhas de projeção até o losango
                ax.plot([p[0], dp[0]], [p[1], dp[1]], ls=":", lw=0.8,
                        color=color, alpha=0.55, zorder=2)
            pts.append(dp)
            plotted.append((dp, s.label))
        for x, y in pts:
            ax.scatter([x], [y], s=110, color=color, edgecolors="black",
                       linewidths=1.0, zorder=5)
        if pts:
            handles.append(plt.Line2D([], [], marker="o", ls="", markersize=10,
                                      markerfacecolor=color, markeredgecolor="black",
                                      markeredgewidth=1.0, label=str(s.label)))

    if labels:
        _label_points(ax, [p[0][0] for p in plotted], [p[0][1] for p in plotted],
                      [p[1] for p in plotted])
    if handles and len(handles) <= 14:
        ax.legend(handles=handles, title="Amostras", loc="upper right",
                  bbox_to_anchor=(1.0, 1.0), frameon=True, fontsize=11,
                  title_fontsize=12, labelspacing=0.6, borderpad=0.8)

    ax.set_xlim(-0.30, 3.30)
    ax.set_ylim(-0.30, _DIA_CY + _H + 0.45)
    ax.set_title(title or "Diagrama de Piper", fontsize=18, fontweight="bold", pad=14)
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
