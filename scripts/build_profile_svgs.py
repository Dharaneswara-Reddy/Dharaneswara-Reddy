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

# Four saturated blocks carry the numbers. They are the same in both themes,
# so the card has one identity whichever mode GitHub serves - and a bright card
# is the thing that stands out, because nearly every profile banner is dark.
BLOCKS = ["#1B3BFF", "#FF4D2E", "#F5A300", "#00A86B"]   # cobalt, vermilion, amber, emerald

DARK = dict(bg="#101014", ink="#FAF7F0", dim="#9A968E", accent="#FF4D2E",
            rule="#26262C", onblock="#FFFFFF")
LIGHT = dict(bg="#FFFBF2", ink="#12121A", dim="#6B675E", accent="#FF4D2E",
             rule="#E7DFCF", onblock="#FFFFFF")


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
    for i, (num, label, sub) in enumerate(s):
        x = 712 + (i % 2) * 206
        y = 112 + (i // 2) * 134
        fill = BLOCKS[i % len(BLOCKS)]
        tiles.append(f"""
  <rect x="{x}" y="{y}" width="186" height="112" rx="4" fill="{fill}"/>
  <text x="{x+20}" y="{y+52}" font-size="33" font-weight="800" font-family="{MONO}" fill="{c['onblock']}">{esc(num)}</text>
  <text x="{x+20}" y="{y+78}" font-size="12.5" font-weight="700" fill="{c['onblock']}">{esc(label)}</text>
  <text x="{x+20}" y="{y+96}" font-size="11.5" fill="{c['onblock']}" opacity="0.82">{esc(sub)}</text>""")

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{SANS}" role="img" aria-label="Venkata Dharaneswara Reddy Palle — AI/ML Engineer, open to work">
<rect width="{W}" height="{H}" fill="{c['bg']}"/>
<rect x="0" y="0" width="{W/4}" height="7" fill="{BLOCKS[0]}"/>
<rect x="{W/4}" y="0" width="{W/4}" height="7" fill="{BLOCKS[1]}"/>
<rect x="{W/2}" y="0" width="{W/4}" height="7" fill="{BLOCKS[2]}"/>
<rect x="{3*W/4}" y="0" width="{W/4}" height="7" fill="{BLOCKS[3]}"/>

<!-- ===== left: who, in a scale that drops ===== -->
<text x="68" y="96" font-size="13" font-weight="700" letter-spacing="3.6" font-family="{MONO}" fill="{BLOCKS[1]}">AI / ML ENGINEER</text>

<text x="64" y="172" font-size="52" font-weight="700" letter-spacing="-1" textLength="580" lengthAdjust="spacingAndGlyphs" fill="{c['ink']}">Venkata Dharaneswara</text>
<text x="64" y="228" font-size="52" font-weight="700" letter-spacing="-1" textLength="318" lengthAdjust="spacingAndGlyphs" fill="{c['ink']}">Reddy Palle</text>

<line x1="68" y1="262" x2="172" y2="262" stroke="{BLOCKS[1]}" stroke-width="5"/>

<text x="68" y="300" font-size="16" textLength="556" lengthAdjust="spacingAndGlyphs" fill="{c['dim']}">I build machine learning systems end to end — measured before</text>
<text x="68" y="324" font-size="16" textLength="556" lengthAdjust="spacingAndGlyphs" fill="{c['dim']}">they are trusted, calibrated before they ship, monitored after.</text>

<text x="68" y="358" font-size="13.5" textLength="568" lengthAdjust="spacingAndGlyphs" fill="{c['dim']}">Final year, B.Tech Artificial Intelligence &amp; Data Science · Amrita Bengaluru · 2027</text>

<!-- open to work -->
<rect x="64" y="382" width="190" height="34" rx="17" fill="none" stroke="{BLOCKS[3]}"/>
<circle cx="86" cy="399" r="4.5" fill="{BLOCKS[3]}"/>
<text x="102" y="404" font-size="12.5" font-weight="700" letter-spacing="1.4" font-family="{MONO}" fill="{BLOCKS[3]}">OPEN TO WORK</text>

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
