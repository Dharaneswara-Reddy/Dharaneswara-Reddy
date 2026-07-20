#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style contribution heatmap SVG:
rounded colored boxes in classic 53-week x 7-day grid, revealed with a
diagonal slide-down animation, Less->More legend, and real stats footer.
"""
import datetime, json, os

HERE = os.path.dirname(__file__)
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP, STEP = 12, 3, 15
PAD, LEFT_LABEL_W, TOP_LABEL_H, TITLEBAR_H = 22, 30, 20, 30
BG, BG2, FRAME = "#0a0e14", "#0d1420", "#1f6feb"
MUTED, TEXT, ACCENT, GREEN, GOLD = "#7d8590", "#e6edf3", "#22d3ee", "#39d353", "#f2cc60"
COL_T, ROW_T, CELL_DUR = 0.018, 0.045, 0.42

def level_for(c):
    if c == 0: return 0
    if c <= 5: return 1
    if c <= 15: return 2
    if c <= 30: return 3
    if c <= 50: return 4
    return 5

def build_grid(days):
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    grid, col = [], [None] * lead
    for d in days:
        dt = datetime.date.fromisoformat(d["date"])
        wd = (dt.weekday() + 1) % 7
        while len(col) < wd: col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7: grid.append(col); col = []
    if col:
        while len(col) < 7: col.append(None)
        grid.append(col)
    return grid

def render(data):
    days, grid = data["days"], build_grid(data["days"])
    n_cols, art_w, art_h = len(grid), len(grid) * STEP, 7 * STEP

    month_labels, seen = [], set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None: continue
            dt = datetime.date.fromisoformat(cell[0])
            key = (dt.year, dt.month)
            if key not in seen and dt.day <= 7: seen.add(key); month_labels.append((ci, dt.strftime("%b")))
            break

    cw = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    ch = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    css = f"@keyframes cell{{0%{{opacity:0;transform:translateY(-6px)}}100%{{opacity:1;transform:translateY(0)}}}}.c{{opacity:0;animation:cell {CELL_DUR:.2f}s cubic-bezier(.2,.8,.2,1) both;}}"

    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{cw}" height="{ch}" viewBox="0 0 {cw} {ch}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
         f'<style>{css}</style>',
         f'<defs><linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
         f'<rect width="{cw}" height="{ch}" rx="12" fill="url(#hbg)"/>',
         f'<rect x="0.5" y="0.5" width="{cw-1}" height="{ch-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
         f'<line x1="0" y1="{TITLEBAR_H}" x2="{cw}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>']
    for i, dc in enumerate(["#ff5f56","#ffbd2e","#27c93f"]):
        p.append(f'<circle cx="{PAD+i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dc}"/>')
    p.append(f'<text x="{cw/2}" y="{TITLEBAR_H/2+4}" fill="{MUTED}" font-size="12" text-anchor="middle">venkat@github: ~/contributions --graph</text>')

    gt, gl = TITLEBAR_H + TOP_LABEL_H, PAD + LEFT_LABEL_W
    for ci, lb in month_labels:
        p.append(f'<text x="{gl+ci*STEP}" y="{TITLEBAR_H+14}" fill="{MUTED}" font-size="10">{lb}</text>')
    for wi, wn in [(1,"Mon"),(3,"Wed"),(5,"Fri")]:
        p.append(f'<text x="{PAD}" y="{gt+wi*STEP+CELL*0.78:.1f}" fill="{MUTED}" font-size="9">{wn}</text>')

    for ci, column in enumerate(grid):
        gx = gl + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None: continue
            ds, cnt, lvl = cell
            gy = gt + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            pl = "s" if cnt != 1 else ""
            p.append(f'<rect class="c" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s"><title>{ds}: {cnt} contribution{pl}</title></rect>')

    ly = gt + art_h + 6
    lx = cw - PAD - (len(PALETTE) * (CELL - 1) + 70)
    p.append(f'<text x="{lx}" y="{ly+CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    bx = lx + 8
    for lvl, color in enumerate(PALETTE):
        p.append(f'<rect x="{bx}" y="{ly}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>')
        bx += CELL
    p.append(f'<text x="{bx+4}" y="{ly+CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')

    sy = ly + CELL + 14
    p.append(f'<line x1="0" y1="{sy}" x2="{cw}" y2="{sy}" stroke="{FRAME}" stroke-opacity="0.25"/>')

    cs, ls = data["current_streak"]["length"], data["longest_streak"]["length"]
    total, best, rng = data["total_contributions"], data["best_day"], data["range"]
    ty = sy + 24
    p.append(f'<text x="{PAD}" y="{ty}" font-size="13" fill="{GREEN}"><tspan font-weight="700">{total:,}</tspan><tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    p.append(f'<text x="{cw-PAD}" y="{ty}" font-size="12" fill="{MUTED}" text-anchor="end">{rng["start"]} &#8594; {rng["end"]}</text>')
    ty += 24
    p.append(f'<text x="{PAD}" y="{ty}" font-size="13" fill="{MUTED}">current streak <tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan><tspan fill="{MUTED}">   &#183;   longest </tspan><tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    p.append(f'<text x="{cw-PAD}" y="{ty}" font-size="12" fill="{MUTED}" text-anchor="end">best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')
    p.append("</svg>")
    return "".join(p)

if __name__ == "__main__":
    data = json.load(open(IN_PATH))
    svg = render(data)
    with open(OUT_PATH, "w") as f: f.write(svg)
    print(f"wrote {OUT_PATH} ({len(svg)} bytes)")
