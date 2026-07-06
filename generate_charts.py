# -*- coding: utf-8 -*-
"""Gráficas ejecutivas WWB — estética editorial (referencia NYT), colores de marca."""
import os
import sys
from pathlib import Path

# el mapa (C4) necesita geopandas/pyproj; si se corre con el Python de QGIS,
# PROJ no encuentra sus datos a menos que se apunte explícitamente
_proj_data = Path(sys.prefix).parent.parent / "share" / "proj"
if _proj_data.exists():
    os.environ.setdefault("PROJ_DATA", str(_proj_data))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import geopandas as gpd

# ---- Paleta WWB ----
AZUL      = "#223581"   # jefas / serie protagonista
LAVANDA   = "#869EE5"   # jefes / serie comparación
AMARILLO  = "#FFB700"   # acento / dato clave
BEIGE     = "#E8DED6"   # neutro
TINTA     = "#1D1D1B"   # texto principal
GRIS      = "#6B6B6B"   # texto tenue
HUESO     = "#FAFAFA"

rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 12.5,
    "text.color": TINTA,
    "axes.edgecolor": TINTA,
    "figure.dpi": 160,
    "svg.fonttype": "none",
})

def pct(v, dec=1):
    s = f"{v:.{dec}f}".rstrip("0").rstrip(".") if dec else f"{v:.0f}"
    return s.replace(".", ",") + "%"

def save(fig, name):
    fig.savefig(f"assets/graficos/{name}", dpi=160, bbox_inches="tight",
                transparent=True, pad_inches=0.12)
    plt.close(fig)
    print("ok:", name)

# =========================================================
# C1 — Línea: ascenso de la jefatura femenina vs. descenso de la masculina
# =========================================================
fig, ax = plt.subplots(figsize=(9.6, 4.7))
x  = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
yf = [32.7, 32.4, 34.4, 34.6, 34.7, 35.3, 34.8, 37.3, 38.4, 39.8, 43.1, 44.2, 45.4, 46.5, 46.4]  # jefas
ym = [67.3, 67.6, 65.6, 65.4, 65.3, 64.7, 65.2, 62.7, 61.6, 60.2, 56.9, 55.8, 54.6, 53.5, 53.6]  # jefes

# banda pandemia
ax.axvspan(2020, 2020.9, color=BEIGE, alpha=0.55, zorder=0)
ax.text(2020.45, 30.4, "Pandemia", ha="center", va="center",
        fontsize=10.5, color=GRIS)

# línea paridad
ax.axhline(50, ls=(0, (2, 3)), lw=1.1, color=GRIS, alpha=0.7, zorder=1)
ax.text(2010, 50.6, "Paridad (50%)", fontsize=10.5, color=GRIS, va="bottom")

# línea de comparación: jefatura masculina (lavanda)
ax.plot(x, ym, color=LAVANDA, lw=2.4, zorder=2, solid_capstyle="round")
ax.scatter(x, ym, s=26, color=LAVANDA, zorder=3)

# línea protagonista: jefatura femenina (azul)
ax.plot(x, yf, color=AZUL, lw=3, zorder=3, solid_capstyle="round")
ax.scatter(x[:-1], yf[:-1], s=30, color=AZUL, zorder=4)
ax.scatter([x[-1]], [yf[-1]], s=150, color=AMARILLO, edgecolor=AZUL,
           linewidth=2.4, zorder=5)

# etiquetas de serie (a la derecha y debajo del valor del último punto)
ax.annotate("Jefas\n(mujeres)", (x[-1], yf[-1]), textcoords="offset points",
            xytext=(16, -15), ha="left", va="top", fontsize=10,
            fontweight="bold", color=AZUL, linespacing=1.15)
ax.annotate("Jefes\n(hombres)", (x[-1], ym[-1]), textcoords="offset points",
            xytext=(16, 16), ha="left", va="bottom", fontsize=10,
            fontweight="bold", color=LAVANDA, linespacing=1.15)

# anotaciones de valor en cada punto de ambas series
# (el año que precede a un valor muy próximo baja su etiqueta para no chocar con el siguiente)
push_down = {2010, 2024}
for xi, yi in zip(x, yf):
    is_last = (xi == x[-1])
    dy, va = (-11, "top") if xi in push_down else (9, "center")
    ax.annotate(pct(yi), (xi, yi), textcoords="offset points",
                xytext=(0, dy), ha="center", va=va,
                fontsize=11.5 if is_last else 8.3,
                fontweight="bold", color=AZUL)
for xi, yi in zip(x, ym):
    is_last = (xi == x[-1])
    dy, va = (-11, "top") if xi in push_down else (9, "center")
    ax.annotate(pct(yi), (xi, yi), textcoords="offset points",
                xytext=(0, dy), ha="center", va=va,
                fontsize=10.5 if is_last else 8.3,
                fontweight="bold", color=LAVANDA)

# etiquetas de año (todas, tamaño reducido para que entren todas)
for xi in x:
    ax.annotate(str(xi), (xi, 28.6), textcoords="offset points",
                xytext=(0, -4), ha="center", fontsize=8.5, color=GRIS)

ax.set_ylim(28, 71)
ax.set_xlim(2009.2, 2027.4)
for sp in ["top", "right", "bottom", "left"]:
    ax.spines[sp].set_visible(False)
ax.set_xticks([]); ax.set_yticks([])
ax.margins(x=0.02)
save(fig, "c1_crecimiento.png")

# =========================================================
# C2 — Barras 100% apiladas: distribución por decil
# =========================================================
fig, ax = plt.subplots(figsize=(9.6, 3.5))
cats = ["Decil 1\n(más pobre)", "Decil 10\n(más rico)"]
mujeres = [54.0, 41.3]
hombres = [46.0, 58.7]
ypos = [0, 1]  # decil 1 abajo, decil 10 arriba

for yp, m, h in zip(ypos, mujeres, hombres):
    ax.barh(yp, m, color=AZUL, height=0.52, zorder=3)
    ax.barh(yp, h, left=m, color=LAVANDA, height=0.52, zorder=3)
    ax.text(m/2, yp, pct(m), ha="center", va="center",
            color=HUESO, fontsize=13, fontweight="bold")
    ax.text(m + h/2, yp, pct(h), ha="center", va="center",
            color=AZUL, fontsize=13, fontweight="bold")

ax.set_yticks(ypos)
ax.set_yticklabels(cats, fontsize=11.5, color=TINTA)
ax.set_xlim(0, 100)
ax.set_xticks([])
for sp in ["top", "right", "bottom", "left"]:
    ax.spines[sp].set_visible(False)
ax.tick_params(length=0)

# leyenda
ax.scatter([], [], marker="s", s=90, color=AZUL, label="Jefas (mujeres)")
ax.scatter([], [], marker="s", s=90, color=LAVANDA, label="Jefes (hombres)")
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=2,
          frameon=False, fontsize=11.5, handletextpad=0.4, columnspacing=1.6)
save(fig, "c2_deciles.png")

# =========================================================
# C3 — Small multiples: por qué están fuera del mercado laboral
# =========================================================
fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.9))

# Mujeres (todas cuidado/oficios -> azul)
mw_lbl = ["Oficios del hogar", "Cuidar niños mayores de 5", "Cuidar niños menores de 5"]
mw_val = [45.2, 12.3, 10.1]
mw_col = [AZUL, AZUL, AZUL]
# Hombres (ciclo de vida -> beige ; oficios/cuidado -> azul)
mn_lbl = ["Pensionado", "Se considera adulto mayor", "Oficios del hogar", "Cuidado infantil"]
mn_val = [37.0, 31.7, 12.0, 2.0]
mn_txt = ["37,0%", "31,7%", "12,0%", "<2%"]
mn_col = [BEIGE, BEIGE, AZUL, AZUL]

def panel(ax, labels, vals, cols, title, txts=None):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    labels = [labels[i] for i in order]; vals = [vals[i] for i in order]
    cols = [cols[i] for i in order]
    if txts: txts = [txts[i] for i in order]
    yp = range(len(vals))
    ax.barh(list(yp), vals, color=cols, height=0.62, zorder=3,
            edgecolor=AZUL, linewidth=[0 if c!=BEIGE else 0.8 for c in cols])
    for i, v in zip(yp, vals):
        t = txts[i] if txts else pct(v)
        ax.text(v + 1.4, i, t, va="center", fontsize=11.5,
                fontweight="bold", color=TINTA)
    ax.set_yticks(list(yp))
    ax.set_yticklabels(labels, fontsize=10.8, color=TINTA)
    ax.set_xlim(0, 55)
    ax.set_xticks([])
    for sp in ["top", "right", "bottom", "left"]:
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold",
                 color=AZUL, pad=10)

panel(axes[0], mw_lbl, mw_val, mw_col, "Mujeres")
panel(axes[1], mn_lbl, mn_val, mn_col, "Hombres", mn_txt)

# leyenda de color (qué codifica)
axes[1].scatter([], [], marker="s", s=90, color=AZUL, label="Cuidado y oficios del hogar")
axes[1].scatter([], [], marker="s", s=90, color=BEIGE, edgecolor=AZUL,
                linewidth=0.8, label="Ciclo de vida (pensión / edad)")
fig.legend(*axes[1].get_legend_handles_labels(), loc="lower center",
           bbox_to_anchor=(0.5, -0.06), ncol=2, frameon=False,
           fontsize=11, handletextpad=0.4, columnspacing=1.8)
plt.subplots_adjust(wspace=0.55)
save(fig, "c3_mercado_laboral.png")

# =========================================================
# C4 — Mapa de coropletas: variación de la jefatura femenina por departamento (2019–2025)
# =========================================================
ROJO_MAPA   = "#D55947"   # retrocede (paleta secundaria WWB, "rojos")
ROJO_TEXTO  = "#A73B2A"   # variante oscurecida para texto legible
NEUTRO_MAPA = "#F0EBE5"   # punto medio "sin cambio" (neutro, no beige de marca)

datos_dpto = {
    "91": 2.44, "05": 2.25, "81": -1.88, "08": -0.38, "11": -2.77,
    "13": 2.57, "15": -2.36, "17": -1.28, "18": -3.72, "85": -4.50,
    "19": 3.51, "20": 0.92, "27": 7.72, "23": -1.13, "25": -4.79,
    "94": -0.19, "95": 3.79, "41": 1.37, "44": 3.32, "47": -5.90,
    "50": -1.99, "52": 1.01, "54": -0.07, "86": 6.08, "63": 0.25,
    "66": 0.73, "88": 2.79, "68": -0.97, "70": -0.16, "73": 0.40,
    "76": 3.55, "97": 2.49, "99": -1.69,
}

geo = gpd.read_file("assets/data/colombia-dptos.geojson")
geo["dif"] = geo["DPTO_CCDGO"].map(datos_dpto)
vmin, vmax = geo["dif"].min(), geo["dif"].max()

cmap = LinearSegmentedColormap.from_list("wwb_div", [ROJO_MAPA, NEUTRO_MAPA, AZUL])
norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

def pp(v):
    return f"{v:+.2f}".replace(".", ",") + " p.p."

fig, ax = plt.subplots(figsize=(8.4, 9.4))
geo.plot(column="dif", cmap=cmap, norm=norm, ax=ax,
         edgecolor="white", linewidth=0.7, zorder=2)
ax.set_axis_off()
ax.set_aspect("equal")

# etiquetas directas: los mayores avances y los mayores retrocesos
destacados = {
    "Chocó":           ("27", AZUL,       (44, 24)),
    "Putumayo":        ("86", AZUL,       (62, 26)),
    "Guaviare":        ("95", AZUL,       (46, 10)),
    "Valle del Cauca": ("76", AZUL,       (-58, -4)),
    "Magdalena":       ("47", ROJO_TEXTO, (18, 26)),
    "Cundinamarca":    ("25", ROJO_TEXTO, (48, -2)),
    "Casanare":        ("85", ROJO_TEXTO, (52, 18)),
    "Caquetá":         ("18", ROJO_TEXTO, (-58, -46)),
}
for nombre, (cod, color, (dx, dy)) in destacados.items():
    row = geo.loc[geo["DPTO_CCDGO"] == cod].iloc[0]
    pt = row.geometry.representative_point()
    ha = "center" if dx == 0 else ("left" if dx > 0 else "right")
    ax.plot(pt.x, pt.y, "o", ms=4.5, color=TINTA, mec="white", mew=0.8, zorder=4)
    ax.annotate(f"{nombre}\n{pp(row['dif'])}", (pt.x, pt.y),
                textcoords="offset points", xytext=(dx, dy),
                ha=ha, va="center", fontsize=10, fontweight="bold",
                color=color, linespacing=1.35, zorder=5,
                arrowprops=dict(arrowstyle="-", color=TINTA, lw=0.7,
                                 shrinkA=0, shrinkB=6,
                                 relpos=(0 if dx > 0 else 1, 0.5)))

x0, x1 = ax.get_xlim()
w = x1 - x0
ax.set_xlim(x0 - 0.10 * w, x1 + 0.14 * w)

# leyenda: barra de degradado horizontal (reemplaza el colorbar por defecto de matplotlib)
leg = fig.add_axes([0.32, 0.055, 0.4, 0.016])
grad = np.linspace(vmin, vmax, 256).reshape(1, -1)
leg.imshow(grad, aspect="auto", cmap=cmap, norm=norm, extent=[vmin, vmax, 0, 1])
leg.set_yticks([])
leg.set_xticks([vmin, 0, vmax])
leg.set_xticklabels([pp(vmin), "Sin cambio", pp(vmax)])
leg.tick_params(length=0, labelsize=10)
for lbl in leg.get_xticklabels():
    lbl.set_color(GRIS)
for sp in leg.spines.values():
    sp.set_visible(False)

save(fig, "c4_departamentos.png")

print("=== todas las gráficas generadas ===")
