"""Build the profile banner: dark.svg and light.svg.

A poster, not a terminal dump. The earlier version printed ten key/value rows
at one type size with dotted leaders between them, which read as noise and gave
the eye nowhere to land. This one has a single focal point - the name - a scale
that drops from it, four numbers worth looking at, and a lot of empty space.

No portrait: it was a dithered approximation of a face that said nothing the
words do not.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DARK_SVG_PATH = os.path.join(ROOT, "dark.svg")
LIGHT_SVG_PATH = os.path.join(ROOT, "light.svg")
CONTRIB_PATH = os.path.join(ROOT, "data", "contributions.json")

W, H = 1180, 470
SANS = "'Segoe UI',Inter,ui-sans-serif,system-ui,-apple-system,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

DARK = dict(bg="#0B1A24", ink="#F4EFE6", dim="#93A7A8", accent="#FF6B4A",
            accent2="#5FB3A8", good="#5FB3A8", rule="#18323C", tile="#0F2430")
LIGHT = dict(bg="#FBF9F5", ink="#10222B", dim="#5C7076", accent="#D9472A",
             accent2="#2E7D74", good="#2E7D74", rule="#E3DED3", tile="#F3EFE7")


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def contributions():
    try:
        with open(CONTRIB_PATH) as f:
            return json.load(f).get("total_contributions")
    except Exception:
        return None


def stats():
    """Four numbers that mean something, largest first."""
    out = [("91.49%", "IEEE-published accuracy", "best prior 82%"),
           ("31,000+", "teams at Meta PyTorch", "Grand Finalist"),
           ("5", "systems shipped", "end to end · Go, Python, AWS")]
    total = contributions()
    out.insert(0, (f"{total:,}" if total else "1,000+", "contributions this year", "and counting"))
    return out


# Kept inside the card width: roughly 140 characters at 12px mono.
STACK = ("Python · Go · SQL   ·   PyTorch · scikit-learn · pandas   ·   "
         "LangGraph · RAG · LLMs   ·   PostgreSQL · PySpark · Databricks   ·   "
         "Docker · AWS · MLflow")


def build(c):
    s = stats()
    tiles = []
    # two columns of two, on the right half
    for i, (num, label, sub) in enumerate(s):
        x = 712 + (i % 2) * 206
        y = 112 + (i // 2) * 134
        tiles.append(f'''
  <rect x="{x}" y="{y}" width="186" height="112" rx="12" fill="{c['tile']}" stroke="{c['rule']}"/>
  <rect x="{x}" y="{y}" width="186" height="3" rx="1.5" fill="{c['accent']}" opacity="0.85"/>
  <text x="{x+22}" y="{y+56}" font-size="34" font-weight="700" font-family="{MONO}" fill="{c['accent']}">{esc(num)}</text>
  <text x="{x+22}" y="{y+80}" font-size="12.5" font-weight="600" fill="{c['ink']}">{esc(label)}</text>
  <text x="{x+22}" y="{y+98}" font-size="11.5" fill="{c['dim']}">{esc(sub)}</text>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="Venkata Dharaneswara Reddy Palle — AI/ML Engineer, open to work">
<rect width="{W}" height="{H}" fill="{c['bg']}"/>
<rect x="0" y="0" width="{W}" height="5" fill="{c['accent']}"/>

<!-- ===== left: who, in a scale that drops ===== -->
<text x="68" y="96" font-size="13" font-weight="700" letter-spacing="3.6" font-family="{MONO}" fill="{c['accent']}">AI / ML ENGINEER</text>

<text x="64" y="172" font-size="52" font-weight="700" letter-spacing="-1" fill="{c['ink']}">Venkata Dharaneswara</text>
<text x="64" y="228" font-size="52" font-weight="700" letter-spacing="-1" fill="{c['ink']}">Reddy Palle</text>

<line x1="68" y1="262" x2="172" y2="262" stroke="{c['accent']}" stroke-width="4"/>

<text x="68" y="300" font-size="16" fill="{c['dim']}">I build machine learning systems end to end — measured before</text>
<text x="68" y="324" font-size="16" fill="{c['dim']}">they are trusted, calibrated before they ship, monitored after.</text>

<text x="68" y="358" font-size="13.5" fill="{c['dim']}">Final year, B.Tech Artificial Intelligence &amp; Data Science · Amrita Bengaluru · 2027</text>

<!-- open to work -->
<rect x="64" y="382" width="190" height="34" rx="17" fill="none" stroke="{c['good']}"/>
<circle cx="86" cy="399" r="4.5" fill="{c['good']}"/>
<text x="102" y="404" font-size="12.5" font-weight="700" letter-spacing="1.4" font-family="{MONO}" fill="{c['good']}">OPEN TO WORK</text>

<text x="272" y="404" font-size="12.5" font-family="{MONO}" fill="{c['dim']}">dharaneswar339@gmail.com · in/palle-venkata-reddy</text>

<!-- ===== right: four numbers ===== -->
<line x1="676" y1="66" x2="676" y2="396" stroke="{c['rule']}"/>
{''.join(tiles)}

<!-- ===== stack, one quiet line across the foot ===== -->
<line x1="64" y1="430" x2="{W-64}" y2="430" stroke="{c['rule']}"/>
<text x="64" y="452" font-size="12" font-family="{MONO}" fill="{c['dim']}">{esc(STACK)}</text>
</svg>
'''


def main():
    with open(DARK_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(build(DARK))
    with open(LIGHT_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(build(LIGHT))
    print("wrote dark.svg and light.svg")


if __name__ == "__main__":
    main()
