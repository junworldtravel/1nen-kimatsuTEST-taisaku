# ⑤ 地図で整理（p.91〜92）の白地図：アフリカ州・北アメリカ州・南アメリカ州・オセアニア州
# 出力: out/{af,na,sa,oc}_map.webp/.json（pos は画像に対する割合）
import sys, json, os, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, box
from shapely.ops import nearest_points
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from pyproj import Transformer
from PIL import Image

D = sys.argv[1]
sys.path.insert(0, D + "/scripts")
import content_world as W
from content_v3 import CIRC

for f in ["/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
    fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Sans CJK JP"
SEA, LANDC, LINE, INK = "#E4EEF4", "#FFFFFF", "#6E6E6E", "#111111"
RIVER, AREA, AREA_E, MT, MT_E = "#2F7FC1", "#CFCFCF", "#8F8F8F", "#E9D3B4", "#9C6B3A"
G50 = gpd.read_file(D + "/map/ne_50m_admin_0_countries.geojson")
RG = gpd.read_file(D + "/map/ne_10m_geography_regions_polys.geojson"); RG["UN"] = RG.NAME.str.upper()
RV = gpd.read_file(D + "/map/ne_50m_rivers_lake_centerlines.geojson")
LK = gpd.read_file(D + "/map/ne_50m_lakes.geojson")
RF = gpd.read_file(D + "/map/ne_10m_reefs.geojson")
DPI = 200

def fit_frame(tf, pts, aspect, pad=0.03):
    xs, ys = tf.transform([p[0] for p in pts], [p[1] for p in pts])
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = x1 - x0, y1 - y0; x0 -= pad * w; x1 += pad * w; y0 -= pad * h; y1 += pad * h
    w, h = x1 - x0, y1 - y0
    if w / h > aspect: nh = w / aspect; cy = (y0 + y1) / 2; y0, y1 = cy - nh / 2, cy + nh / 2
    else: nw = h * aspect; cx = (x0 + x1) / 2; x0, x1 = cx - nw / 2, cx + nw / 2
    return x0, y0, x1, y1

def region(names):
    g = RG[RG.UN.isin([n.upper() for n in names])]
    assert len(g) >= len(names), (names, g.NAME.tolist())
    return g

def snap(anchor, geoms):
    p = Point(anchor); best = min(geoms, key=lambda g: g.distance(p))
    q = nearest_points(best, p)[0]; return (q.x, q.y)

def draw(name, data, crs, view_pts, size, clip_boxes, areas=(), mts=(), rivers=(), lakes=(), reefs=None, dashed=(), snaps=(), notes=()):
    tf = Transformer.from_crs(4326, crs, always_xy=True)
    AW, AH = size
    x0, y0, x1, y1 = fit_frame(tf, view_pts, AW / AH)
    frame = box(x0, y0, x1, y1)
    gp = pd.concat([G50.clip(b) for b in clip_boxes]); gp = gpd.GeoDataFrame(gp, crs=4326).to_crs(crs)
    gp = gp[gp.geometry.is_valid & gp.geometry.intersects(frame)].copy(); gp["geometry"] = gp.geometry.intersection(frame)
    land = gp.geometry.union_all()
    fig = plt.figure(figsize=(AW, AH), dpi=DPI); ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor(SEA)
    gp.plot(ax=ax, color=LANDC, edgecolor="#9A9A9A", linewidth=0.45)
    # 緯線・経線（赤道は実線）
    for lon in range(-180, 181, 30):
        xs, ys = tf.transform(np.full(120, lon), np.linspace(-70, 85, 120)); ax.plot(xs, ys, color="#9DB3C2", lw=0.3, ls=(0, (2, 2)), zorder=0.5)
    for lat in range(-60, 90, 30):
        xs, ys = tf.transform(np.linspace(-180, 180, 720), np.full(720, lat))
        ax.plot(xs, ys, color="#7E9AAE" if lat == 0 else "#9DB3C2", lw=0.8 if lat == 0 else 0.3, ls="-" if lat == 0 else (0, (2, 2)), zorder=0.5)
    cut = region(list(dashed)).to_crs(crs).geometry.buffer(0).union_all() if dashed else None
    for nm in areas:
        g = region([nm]).to_crs(crs); g["geometry"] = g.geometry.buffer(0).intersection(land)
        if cut is not None: g["geometry"] = g.geometry.difference(cut)
        g.plot(ax=ax, facecolor=AREA, edgecolor=AREA_E, linewidth=0.5, alpha=0.9, zorder=1.4)
    for nm in dashed:
        g = region([nm]).to_crs(crs); g["geometry"] = g.geometry.buffer(0).intersection(land)
        g.plot(ax=ax, facecolor="none", edgecolor="#555555", linewidth=1.1, linestyle=(0, (3, 2)), zorder=1.6)
    for nm in mts:
        g = region([nm]).to_crs(crs); g["geometry"] = g.geometry.buffer(0).intersection(land)
        g.plot(ax=ax, facecolor=MT, edgecolor=MT_E, linewidth=0.6, zorder=1.5)
    rv = RV[RV.name.isin(rivers)].to_crs(crs); rv.plot(ax=ax, color=RIVER, linewidth=1.6, zorder=2)
    lk = LK[LK.name.isin(lakes)].to_crs(crs); lk.plot(ax=ax, color="#9CC7E8", edgecolor=RIVER, linewidth=0.6, zorder=2.1)
    if reefs is not None:
        rf = RF.clip(reefs).to_crs(crs); rf.plot(ax=ax, color="#C0392B", linewidth=1.6, zorder=2.2)
    for txt, lon, lat in notes:
        x, y = tf.transform(lon, lat); ax.text(x, y, txt, fontsize=8, color="#5A7387", ha="left", va="center", zorder=3)
    # 番号（川は線の上に点を合わせる）
    marks = []
    for lab, a, cat, alt, anchor, circ in data:
        if lab in snaps:
            geoms = list(RV[RV.name.isin(snaps[lab])].geometry) + list(LK[LK.name.isin(snaps[lab])].geometry.boundary)
            anchor = snap(anchor, geoms)
        marks.append((lab, anchor, circ))
    pos = {}
    for lab, anchor, circ in marks:
        ax_, ay_ = tf.transform(*anchor); cx, cy = tf.transform(*(circ or anchor))
        if circ:
            ax.plot([ax_, cx], [ay_, cy], color=INK, lw=0.9, zorder=4); ax.plot([ax_], [ay_], "o", ms=3.2, color=INK, zorder=5)
        ax.scatter([cx], [cy], s=330, facecolor="white", edgecolor=INK, linewidth=1.3, zorder=6)
        t = str(CIRC.index(lab) + 1)
        ax.text(cx, cy, t, fontsize=11.5 * (0.9 if len(t) > 1 else 1), fontweight="bold", ha="center", va="center", color=INK, zorder=7)
        assert x0 < cx < x1 and y0 < cy < y1, (name, lab, "circle outside frame")
    # 凡例
    W_, H_ = x1 - x0, y1 - y0; lx, ly = x0 + W_ * 0.02, y0 + H_ * 0.02; items = []
    if mts: items.append(("rect", MT, MT_E, "山脈"))
    if areas: items.append(("rect", AREA, AREA_E, "砂漠・高原など"))
    if rivers: items.append(("line", RIVER, None, "川"))
    if reefs is not None: items.append(("line", "#C0392B", None, "さんご礁"))
    for k, (kind, c, e, txt) in enumerate(items):
        yy = ly + H_ * 0.045 * k
        if kind == "rect": ax.add_patch(plt.Rectangle((lx, yy), W_ * 0.03, H_ * 0.025, facecolor=c, edgecolor=e, lw=0.6, zorder=8))
        else: ax.plot([lx, lx + W_ * 0.03], [yy + H_ * 0.0125] * 2, color=c, lw=2.0, zorder=8)
        ax.text(lx + W_ * 0.04, yy + H_ * 0.0125, txt, fontsize=9, va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.1", fc=(1, 1, 1, 0.75), ec="none"))
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_xticks([]); ax.set_yticks([]); ax.set_aspect("equal")
    for s in ax.spines.values(): s.set_visible(False)
    fig.canvas.draw(); Wp, Hp = fig.canvas.get_width_height()
    for lab, anchor, circ in marks:
        px, py = ax.transData.transform(tf.transform(*(circ or anchor)))
        pos[lab] = {"x": round(px / Wp, 5), "y": round(1 - py / Hp, 5)}
    out = D + "/out"; os.makedirs(out, exist_ok=True)
    png = f"{out}/{name}.png"; fig.savefig(png, dpi=DPI); plt.close(fig)
    im = Image.open(png).convert("RGB"); im.save(f"{out}/{name}.webp", "WEBP", quality=84, method=6)
    json.dump({"w": im.size[0], "h": im.size[1], "pos": pos}, open(f"{out}/{name}.json", "w"), ensure_ascii=False)
    print(name, im.size, "webp KB", os.path.getsize(f"{out}/{name}.webp") // 1024)

def af():
    draw("af_map", W.AF_MAP, "+proj=laea +lat_0=4 +lon_0=18 +datum=WGS84 +units=m",
         [(-25, 37), (-25, -36), (63, 37), (63, -36), (18, 39), (20, -36)], (9.0, 8.6), [box(-40, -45, 75, 50)],
         areas=["SAHARA"], dashed=["SAHEL"], rivers=["Nile", "Niger", "Congo", "Albert Nile", "Victoria Nile"], lakes=["Lake Victoria"],
         snaps={"⑤": ["Nile"], "⑥": ["Niger"], "⑧": ["Lake Victoria"]})
def na():
    draw("na_map", W.NA_MAP, "+proj=laea +lat_0=47 +lon_0=-100 +datum=WGS84 +units=m",
         [(-168, 66), (-160, 56), (-125, 22), (-80, 8), (-60, 14), (-22, 70), (-40, 83), (-120, 80)], (9.0, 8.6), [box(-180, 0, -10, 85)],
         mts=["ROCKY MOUNTAINS", "APPALACHIAN MTS."], dashed=["GREAT PLAINS"], rivers=["Mississippi", "Rio Grande", "Grande"],
         lakes=["Lake Superior", "Lake Michigan", "Lake Huron", "Lake Erie", "Lake Ontario"],
         snaps={"⑥": ["Mississippi"], "⑪": ["Rio Grande", "Grande"]})
def sa():
    draw("sa_map", W.SA_MAP, "+proj=laea +lat_0=-18 +lon_0=-62 +datum=WGS84 +units=m",
         [(-96, 18), (-96, -57), (-27, 18), (-27, -57)], (7.6, 9.0), [box(-120, -62, -20, 30)],
         areas=["GUIANA HIGHLANDS", "BRAZILIAN HIGHLANDS"], mts=["ANDES"], rivers=["Amazonas", "Paraná"],
         snaps={"⑤": ["Amazonas"]})
def oc():
    draw("oc_map", W.OC_MAP, "+proj=laea +lat_0=-20 +lon_0=155 +datum=WGS84 +units=m",
         [(110, 10), (110, -46), (195, 10), (195, -46)], (10.4, 7.6), [box(95, -60, 180, 25), box(-180, -60, -150, 25)],
         areas=["GREAT SANDY DESERT", "GREAT VICTORIA DESERT", "GREAT ARTESIAN BASIN"], mts=["GREAT DIVIDING RANGE"],
         reefs=box(142, -25, 155, -9))

if __name__ == "__main__":
    which = sys.argv[2:] or ["af", "na", "sa", "oc"]
    for w in which: globals()[w]()
