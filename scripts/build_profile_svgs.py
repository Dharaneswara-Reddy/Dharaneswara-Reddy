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

W, H = 1180, 424
SANS = "'Segoe UI',Inter,ui-sans-serif,system-ui,-apple-system,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

DARK = dict(bg="#0A101F", ink="#F8FAFC", dim="#8C9CB8", accent="#22D3EE",
            accent2="#A78BFA", good="#34D399", rule="#1C2840", tile="#0E1729")
LIGHT = dict(bg="#FFFFFF", ink="#0F172A", dim="#64748B", accent="#0891B2",
             accent2="#7C3AED", good="#059669", rule="#E6EBF2", tile="#F7F9FC")


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
           ("5", "systems shipped end to end", "Go · Python · AWS")]
    total = contributions()
    out.insert(0, (f"{total:,}" if total else "1,000+", "contributions this year", "and counting"))
    return out


STACK = ("Python · Go · SQL   ·   PyTorch · scikit-learn · pandas · NumPy   ·   "
         "LangGraph · RAG · LLMs   ·   PostgreSQL · PySpark · Databricks   ·   "
         "Docker · AWS · Terraform · MLflow")


def build(c):
    s = stats()
    tiles = []
    # two columns of two, on the right half
    for i, (num, label, sub) in enumerate(s):
        x = 706 + (i % 2) * 232
        y = 104 + (i // 2) * 118
        tiles.append(f'''
  <rect x="{x}" y="{y}" width="206" height="94" rx="10" fill="{c['tile']}" stroke="{c['rule']}"/>
  <text x="{x+20}" y="{y+42}" font-size="30" font-weight="700" font-family="{MONO}" fill="{c['accent']}">{esc(num)}</text>
  <text x="{x+20}" y="{y+64}" font-size="12" font-weight="600" fill="{c['ink']}">{esc(label)}</text>
  <text x="{x+20}" y="{y+81}" font-size="11" fill="{c['dim']}">{esc(sub)}</text>''')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="Venkata Dharaneswara Reddy Palle — AI/ML Engineer, open to work">
<rect width="{W}" height="{H}" fill="{c['bg']}"/>
<rect x="0" y="0" width="{W}" height="4" fill="{c['accent']}"/>

<!-- ===== left: who, in a scale that drops ===== -->
<text x="64" y="86" font-size="12" font-weight="700" letter-spacing="3.4" font-family="{MONO}" fill="{c['accent']}">AI / ML ENGINEER</text>

<text x="60" y="150" font-size="44" font-weight="700" letter-spacing="-1" fill="{c['ink']}">Venkata Dharaneswara</text>
<text x="60" y="198" font-size="44" font-weight="700" letter-spacing="-1" fill="{c['ink']}">Reddy Palle</text>

<line x1="64" y1="226" x2="150" y2="226" stroke="{c['accent2']}" stroke-width="3"/>

<text x="64" y="258" font-size="15" fill="{c['dim']}">I build machine learning systems end to end — measured before</text>
<text x="64" y="280" font-size="15" fill="{c['dim']}">they are trusted, calibrated before they ship, monitored after.</text>

<text x="64" y="314" font-size="13" fill="{c['dim']}">Final year, B.Tech Artificial Intelligence &amp; Data Science · Amrita Bengaluru · 2027</text>

<!-- open to work -->
<rect x="60" y="332" width="178" height="30" rx="15" fill="none" stroke="{c['good']}"/>
<circle cx="80" cy="347" r="4" fill="{c['good']}"/>
<text x="94" y="352" font-size="12" font-weight="700" letter-spacing="1.4" font-family="{MONO}" fill="{c['good']}">OPEN TO WORK</text>

<text x="256" y="352" font-size="12" font-family="{MONO}" fill="{c['dim']}">dharaneswar339@gmail.com · in/palle-venkata-reddy</text>

<!-- ===== right: four numbers ===== -->
<line x1="672" y1="58" x2="672" y2="348" stroke="{c['rule']}"/>
{''.join(tiles)}

<!-- ===== stack, one quiet line across the foot ===== -->
<line x1="64" y1="376" x2="{W-64}" y2="376" stroke="{c['rule']}"/>
<text x="64" y="400" font-size="11.5" font-family="{MONO}" fill="{c['dim']}">{esc(STACK)}</text>
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
