"""Build the profile banner: dark.svg and light.svg.

A terminal card, rendered as pure SVG text. There is deliberately no portrait
in it any more: the photo was a dithered approximation that said nothing the
words do not, and it cost half the width.

The two themes are the same drawing with a different palette, so GitHub can
serve whichever matches the reader's mode.
"""
import json
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DARK_SVG_PATH = os.path.join(ROOT, "dark.svg")
LIGHT_SVG_PATH = os.path.join(ROOT, "light.svg")
CONTRIB_PATH = os.path.join(ROOT, "data", "contributions.json")

W, H = 1180, 500
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

DARK = dict(bg="#0A101F", chrome="#111A2E", edge="#1E2A44", label="#22D3EE",
            value="#F8FAFC", dim="#94A3B8", accent="#A78BFA", good="#34D399",
            rule="#1B2740", shadow="0.45")
LIGHT = dict(bg="#FFFFFF", chrome="#F1F5F9", edge="#D8E0EC", label="#0891B2",
             value="#0F172A", dim="#475569", accent="#7C3AED", good="#059669",
             rule="#E2E8F0", shadow="0.10")


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def contributions():
    """Real numbers if the fetch script has run, a safe fallback if not."""
    try:
        with open(CONTRIB_PATH) as f:
            d = json.load(f)
        return d.get("total_contributions"), d.get("active_days")
    except Exception:
        return None, None


IDENTITY = [
    ("Subject", "Venkata Dharaneswara Reddy Palle"),
    ("Role", "AI/ML Engineer"),
    ("Education", "B.Tech Artificial Intelligence & Data Science, 2027"),
    ("Institute", "Amrita Vishwa Vidyapeetham, Bengaluru"),
    ("Experience", "Software Development Co-Op Intern, AlgoUniversity (YC)"),
]

STACK = [
    ("Core.Lang", "Python · Go · Java · SQL"),
    ("Core.ML", "PyTorch · scikit-learn · pandas · NumPy · SHAP"),
    ("Core.LLM", "LangGraph · RAG · Transformers · fine-tuning"),
    ("Core.Data", "PostgreSQL · MongoDB · PySpark · Databricks"),
    ("Core.Infra", "Docker · AWS · Azure · Terraform · MLflow"),
]

BUILDING = [
    ("CodeArena", "online judge · Go, React, sandboxed execution"),
    ("Constitutional AI", "GRPO + QLoRA alignment on an 8GB GPU"),
    ("AI Ops Copilot", "multi-agent RAG · recall@k 0.979"),
    ("Churn ML System", "PR-AUC, calibration, SHAP, drift, retraining"),
    ("durexec", "sharded durable execution engine in Go"),
]


def signals():
    total, days = contributions()
    out = [
        ("IEEE Xplore", "published — 91.49% vs 82% prior"),
        ("Meta PyTorch", "OpenEnv Grand Finalist, 31,000+ teams"),
        ("Competitive", "100+ LeetCode · Codeforces 1112"),
    ]
    if total:
        out.append(("Contributions", f"{total:,} in the last year"
                                     + (f" · {days} active days" if days else "")))
    return out


def leader(label, value, width=74):
    """The dotted run between a label and its value, as a terminal would print."""
    return "." * max(4, width - len(label) - len(value))


def rows(items, x, y, step, c, label_w=120, dotted=True):
    """Key/value lines. Labels in the accent colour, values in the ink colour."""
    out = []
    for i, (k, v) in enumerate(items):
        yy = y + i * step
        out.append(f'<text x="{x}" y="{yy}" font-size="13" fill="{c["label"]}">{esc(k)}</text>')
        if dotted:
            out.append(f'<text x="{x + label_w}" y="{yy}" font-size="13" fill="{c["rule"]}">'
                       f'{leader(k, v)}</text>')
        out.append(f'<text x="{x + 560}" y="{yy}" font-size="13" text-anchor="end" '
                   f'fill="{c["value"]}">{esc(v)}</text>')
    return "\n".join(out)


def stacked(items, x, y, step, c):  # two-line entries for the right column
    out = []
    for i, (k, v) in enumerate(items):
        yy = y + i * step
        out.append(f'<text x="{x}" y="{yy}" font-size="13" font-weight="700" '
                   f'fill="{c["accent"]}">{esc(k)}</text>')
        out.append(f'<text x="{x}" y="{yy + 16}" font-size="12" fill="{c["dim"]}">{esc(v)}</text>')
    return "\n".join(out)


def heading(text, x, y, c):
    return (f'<text x="{x}" y="{y}" font-size="11" letter-spacing="2.2" '
            f'font-weight="700" fill="{c["label"]}">{esc(text)}</text>')


def build(c, theme):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    mid = 612
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{MONO}" role="img" aria-label="Venkata Dharaneswara Reddy Palle — AI/ML Engineer">
<defs>
  <clipPath id="card"><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14"/></clipPath>
</defs>

<rect width="{W}" height="{H}" fill="{c['bg']}"/>
<g clip-path="url(#card)">
  <rect x="8" y="8" width="{W-16}" height="{H-16}" rx="14" fill="{c['bg']}" stroke="{c['edge']}"/>

  <!-- window chrome -->
  <rect x="8" y="8" width="{W-16}" height="38" fill="{c['chrome']}"/>
  <line x1="8" y1="46" x2="{W-8}" y2="46" stroke="{c['edge']}"/>
  <circle cx="34" cy="27" r="6" fill="#FF5F57"/>
  <circle cx="54" cy="27" r="6" fill="#FEBC2E"/>
  <circle cx="74" cy="27" r="6" fill="#28C840"/>
  <text x="{W/2}" y="31" text-anchor="middle" font-size="12" fill="{c['dim']}">venkat@github ~ % ./profile.sh --live</text>
  <text x="{W-28}" y="31" text-anchor="end" font-size="11" fill="{c['good']}">● LIVE</text>

  <!-- left column -->
  {heading("IDENTITY", 40, 78, c)}
  <line x1="40" y1="88" x2="{mid-40}" y2="88" stroke="{c['rule']}"/>
  {rows(IDENTITY, 40, 112, 24, c)}

  {heading("STACK", 40, 248, c)}
  <line x1="40" y1="258" x2="{mid-40}" y2="258" stroke="{c['rule']}"/>
  {rows(STACK, 40, 282, 24, c)}

  <!-- divider -->
  <line x1="{mid}" y1="70" x2="{mid}" y2="{H-66}" stroke="{c['rule']}"/>

  <!-- right column -->
  {heading("BUILDING", mid+36, 78, c)}
  <line x1="{mid+36}" y1="88" x2="{W-40}" y2="88" stroke="{c['rule']}"/>
  {stacked(BUILDING, mid+36, 110, 34, c)}

  {heading("SIGNALS", mid+36, 288, c)}
  <line x1="{mid+36}" y1="298" x2="{W-40}" y2="298" stroke="{c['rule']}"/>
  {stacked(signals(), mid+36, 320, 30, c)}

  <!-- status bar -->
  <line x1="8" y1="{H-54}" x2="{W-8}" y2="{H-54}" stroke="{c['edge']}"/>
  <rect x="8" y="{H-54}" width="{W-16}" height="46" fill="{c['chrome']}"/>
  <text x="40" y="{H-26}" font-size="13" font-weight="700" fill="{c['good']}">● OPEN TO WORK</text>
  <text x="196" y="{H-26}" font-size="13" fill="{c['dim']}">AI/ML engineering roles</text>
  <text x="{W-40}" y="{H-26}" text-anchor="end" font-size="12" fill="{c['dim']}">dharaneswar339@gmail.com · in/palle-venkata-reddy · {stamp}</text>
</g>
</svg>
'''


def main():
    with open(DARK_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(build(DARK, "dark"))
    with open(LIGHT_SVG_PATH, "w", encoding="utf-8") as f:
        f.write(build(LIGHT, "light"))
    print(f"wrote {DARK_SVG_PATH} and {LIGHT_SVG_PATH}")


if __name__ == "__main__":
    main()
