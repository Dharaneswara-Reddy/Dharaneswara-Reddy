"""
Generator script to build theme-aware animated terminal profile SVGs (dark.svg and light.svg)
matching the exact master prompt reference style, using the user's Profile_Pic.png.
"""

import math
import os
import random
import re
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PIC_PATH = os.path.join(ROOT, "Profile_Pic.png")
DARK_SVG_PATH = os.path.join(ROOT, "dark.svg")
LIGHT_SVG_PATH = os.path.join(ROOT, "light.svg")


def compute_dotted_leader(label, value, target_dots=60):
    """Computes a dotted leader string matching the target length."""
    combined_len = len(label) + len(value)
    dots_needed = max(5, target_dots - combined_len)
    return "." * dots_needed


def extract_pixel_runs(im, is_dark_mode=True, grid_w=300, grid_h=320):
    """
    Extracts contiguous horizontal runs of dithered pixels from the image.
    For dark mode, lit subject area produces dots.
    For light mode, dark subject/features produce dots.
    """
    # Composite over background
    if im.mode == "RGBA":
        bg_color = (10, 16, 31, 255) if is_dark_mode else (255, 255, 255, 255)
        bg = Image.new("RGBA", im.size, bg_color)
        comp = Image.alpha_composite(bg, im)
        gray = comp.convert("L")
    else:
        gray = im.convert("L")

    # Crop/resize centered
    w, h = gray.size
    min_dim = min(w, h)
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    gray_cropped = gray.crop((left, top, left + min_dim, top + min_dim))
    gray_res = gray_cropped.resize((grid_w, grid_h), Image.LANCZOS)

    # Convert to array & adjust contrast
    arr = np.array(gray_res, dtype=float) / 255.0

    if is_dark_mode:
        # Boost contrast so face highlights glow nicely on dark panel
        arr = np.clip((arr - 0.45) * 1.4 + 0.55, 0, 1)
        thresh = 0.42
    else:
        # Invert so dark parts become pixels
        arr = 1.0 - arr
        arr = np.clip((arr - 0.45) * 1.4 + 0.55, 0, 1)
        thresh = 0.42

    # Floyd-Steinberg dithering
    dither = arr.copy()
    binary_grid = np.zeros((grid_h, grid_w), dtype=int)

    for y in range(grid_h):
        for x in range(grid_w):
            oldval = dither[y, x]
            newval = 1.0 if oldval > thresh else 0.0
            binary_grid[y, x] = int(newval)
            err = oldval - newval
            if x + 1 < grid_w:
                dither[y, x + 1] += err * 7 / 16
            if y + 1 < grid_h:
                if x - 1 >= 0:
                    dither[y + 1, x - 1] += err * 3 / 16
                dither[y + 1, y] if False else None
                dither[y + 1, x] += err * 5 / 16
                if x + 1 < grid_w:
                    dither[y + 1, x + 1] += err * 1 / 16

    # Extract horizontal runs (M{x} {y}h{w}v1h-{w}z)
    runs = []
    for y in range(grid_h):
        x = 0
        while x < grid_w:
            if binary_grid[y, x] == 1:
                x_start = x
                while x < grid_w and binary_grid[y, x] == 1:
                    x += 1
                run_w = x - x_start
                runs.append((x_start, y, run_w))
            else:
                x += 1
    return runs


def format_runs_to_paths(runs):
    """Combines list of (x, y, w) tuples into SVG path commands."""
    cmd_list = []
    for x, y, w in runs:
        if w == 1:
            cmd_list.append(f"M{x} {y}h1v1h-1z")
        else:
            cmd_list.append(f"M{x} {y}h{w}v1h-{w}z")
    return "".join(cmd_list)


def build_animated_groups(runs, num_groups=60, anim_dur=0.9, total_anim_time=2.0):
    """
    Splits runs randomly across interleaved groups that reveal staggered over time.
    """
    random.seed(42)
    shuffled = list(runs)
    random.shuffle(shuffled)

    group_size = math.ceil(len(shuffled) / num_groups)
    groups_xml = []

    for g_idx in range(num_groups):
        g_runs = shuffled[g_idx * group_size : (g_idx + 1) * group_size]
        if not g_runs:
            continue
        path_d = format_runs_to_paths(g_runs)
        begin_time = (g_idx / num_groups) * total_anim_time + 0.20
        g_str = (
            f'<g opacity="0">'
            f'<animate attributeName="opacity" values="0;1" dur="{anim_dur:.2f}s" '
            f'begin="{begin_time:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines=".4 0 .2 1"/>'
            f'<path d="{path_d}"/>'
            f'</g>'
        )
        groups_xml.append(g_str)

    # Master full path for final static hold at 3.2s
    full_path_d = format_runs_to_paths(runs)
    return "".join(groups_xml), full_path_d


def generate_svg(is_dark_mode=True):
    """Builds complete dark.svg or light.svg file string."""
    im = Image.open(PIC_PATH)
    runs = extract_pixel_runs(im, is_dark_mode=is_dark_mode)
    anim_groups_xml, full_path_d = build_animated_groups(runs)

    bg_canvas = "#070B16" if is_dark_mode else "#F8FAFC"
    panel_grad_start = "#0A101F" if is_dark_mode else "#FFFFFF"
    panel_grad_end = "#0C1426" if is_dark_mode else "#F1F5F9"
    header_bg = "#0B1222" if is_dark_mode else "#EEF2F7"
    header_text_color = "#94A3B8" if is_dark_mode else "#475569"
    box_bg = "#0A101F" if is_dark_mode else "#FFFFFF"
    box_stroke = "rgba(34,211,238,0.35)" if is_dark_mode else "rgba(8,145,178,0.35)"
    title_glow_color = "#22D3EE" if is_dark_mode else "#0891B2"

    accent_stops = (
        """
      <stop offset="0" stop-color="#7C3AED"><animate attributeName="stop-color" values="#7C3AED;#22D3EE;#10B981;#7C3AED" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#22D3EE"><animate attributeName="stop-color" values="#22D3EE;#10B981;#7C3AED;#22D3EE" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#7C3AED;#22D3EE;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    """
        if is_dark_mode
        else """
      <stop offset="0" stop-color="#2563EB"><animate attributeName="stop-color" values="#2563EB;#06B6D4;#10B981;#2563EB" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="0.5" stop-color="#06B6D4"><animate attributeName="stop-color" values="#06B6D4;#10B981;#2563EB;#06B6D4" dur="10s" repeatCount="indefinite"/></stop>
      <stop offset="1" stop-color="#10B981"><animate attributeName="stop-color" values="#10B981;#2563EB;#06B6D4;#10B981" dur="10s" repeatCount="indefinite"/></stop>
    """
    )

    ascii_grad_stops = (
        """
      <stop offset="0" stop-color="#60A5FA"/>
      <stop offset="0.45" stop-color="#A78BFA"/>
      <stop offset="1" stop-color="#22D3EE"/>
    """
        if is_dark_mode
        else """
      <stop offset="0" stop-color="#1D4ED8"/>
      <stop offset="0.45" stop-color="#7C3AED"/>
      <stop offset="1" stop-color="#0891B2"/>
    """
    )

    rect_def_id = "tvdark" if is_dark_mode else "tvlight"
    rect_def_fill = "#A78BFA" if is_dark_mode else "#7C3AED"

    pill_bg = "#4C1D95" if is_dark_mode else "#DBEAFE"
    pill_text = "#E9D5FF" if is_dark_mode else "#1D4ED8"

    label_color = "#22D3EE" if is_dark_mode else "#0891B2"
    dot_color = "rgba(148,163,184,0.35)"
    value_color = "#F8FAFC" if is_dark_mode else "#0F172A"

    rows_data = [
        ("Subject", "Dharaneswara Reddy"),
        ("Role", "AI &amp; Full-Stack Developer"),
        ("Origin", "India"),
        ("Education", "B.Tech CSE"),
        ("Status", "Building + Learning + Shipping"),
        ("ToolChain", "VS Code, Git, Python, C++, Linux"),
        ("Core.Lang", "Python, C++, JavaScript"),
        ("Core.Frontend", "HTML/CSS, React, Tailwind"),
        ("Core.Backend", "Node.js, Express, Python"),
        ("Core.Database", "MongoDB, PostgreSQL, MySQL"),
        ("Core.Infra", "Docker, Vercel, Git"),
        ("divider", "- Contact"),
        ("Grid.Mail", "dharaneswarareddykasireddy@gmail.com"),
        ("Grid.LinkedIn", "dharaneswara-reddy"),
        ("Grid.GitHub", "@Dharaneswara-Reddy"),
        ("Grid.Commits", "406 Total Commits"),
    ]

    rows_xml = []
    y_start = 162
    y_step = 23
    anim_begin = 0.90

    for idx, (label, val) in enumerate(rows_data):
        y_pos = y_start + idx * y_step
        b_time = anim_begin + idx * 0.12

        if label == "divider":
            rows_xml.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{b_time:.2f}s" fill="freeze"/>'
                f'<text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
                f'<tspan fill="#94A3B8">{val} </tspan>'
                f'<tspan fill="{dot_color}">---------------------------------------------------------------------</tspan>'
                f'</text>'
                f'</g>'
            )
        else:
            dots = compute_dotted_leader(label, val, target_dots=68)
            rows_xml.append(
                f'<g opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{b_time:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="-8 0;0 0" dur="0.4s" begin="{b_time:.2f}s" fill="freeze"/>'
                f'<text x="470" y="{y_pos}" font-size="14" textLength="655" lengthAdjust="spacingAndGlyphs" xml:space="preserve">'
                f'<tspan fill="{label_color}">{label} </tspan>'
                f'<tspan fill="{dot_color}">{dots}</tspan>'
                f'<tspan fill="{value_color}" font-weight="600"> {val}</tspan>'
                f'</text>'
                f'</g>'
            )

    system_rows_html = "\n".join(rows_xml)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="610" viewBox="0 0 1180 610" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace" role="img" aria-label="Dharaneswara Reddy — profile.sh --live">
<defs>
<linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
{accent_stops}
</linearGradient>
<linearGradient id="asciiGrad" x1="0" y1="0" x2="0" y2="520" gradientUnits="userSpaceOnUse">
{ascii_grad_stops}
      <animateTransform attributeName="gradientTransform" type="translate" values="0 -120; 0 120; 0 -120" dur="9s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="panelGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{panel_grad_start}"/><stop offset="1" stop-color="{panel_grad_end}"/></linearGradient>
<filter id="glow8" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="8"/></filter>
<filter id="glow3" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="txtGlow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="0.9" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<clipPath id="winClip"><rect x="2" y="2" width="1176" height="606" rx="18"/></clipPath>
</defs>
<rect x="2" y="2" width="1176" height="606" rx="18" fill="{bg_canvas}"/>
<g clip-path="url(#winClip)">
<rect x="2" y="2" width="1176" height="606" fill="url(#panelGrad)"/>
<rect x="2" y="2" width="1176" height="46" fill="{header_bg}"/>
<line x1="2" y1="48" x2="1178" y2="48" stroke="rgba(255,255,255,0.10)"/>
<circle cx="30" cy="25.0" r="5.5" fill="#ff5f56"/>
<circle cx="50" cy="25.0" r="5.5" fill="#ffbd2e"/>
<circle cx="70" cy="25.0" r="5.5" fill="#27c93f"/>
<text x="590.0" y="29.0" text-anchor="middle" font-size="12" fill="{header_text_color}">dharaneswarareddykasireddy@gmail.com - % ./profile.sh --live</text>
<text x="38" y="74" font-size="10" letter-spacing="3" fill="#475569">VISUAL.MAP</text>
<rect x="36" y="84" width="400" height="492" rx="10" fill="none" stroke="{title_glow_color}" stroke-width="2" opacity="0.45" filter="url(#glow3)"/>
<rect x="36" y="84" width="400" height="492" rx="10" fill="{box_bg}" stroke="{box_stroke}"/>

<g transform="translate(50,86) scale(1.2400,1.4471)" fill="url(#asciiGrad)" shape-rendering="crispEdges">
<set attributeName="opacity" to="0" begin="3.2s"/>
{anim_groups_xml}
</g>

<g transform="translate(50,86) scale(1.2400,1.4471)" fill="url(#asciiGrad)" shape-rendering="crispEdges" opacity="0">
<set attributeName="opacity" to="1" begin="3.2s"/>
<path d="{full_path_d}"/>
</g>

<defs><rect id="{rect_def_id}" width="2.4" height="1.7" fill="{rect_def_fill}"/></defs>

<text x="470" y="106" font-size="13" letter-spacing="2" fill="{label_color}" filter="url(#txtGlow)">SYSTEM.INFO</text>
<line x1="566" y1="102" x2="1061" y2="102" stroke="rgba(255,255,255,0.10)"/>
<text x="1125" y="106" text-anchor="end" font-size="12" fill="#F87171" font-weight="700"><tspan>&#9679;</tspan> LIVE<animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/></text>

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.6s" fill="freeze"/>
<rect x="470" y="122" width="345" height="22" rx="4" fill="{pill_bg}"/>
<text x="479" y="137" font-size="13" font-weight="700" fill="{pill_text}">dharaneswarareddykasireddy@gmail.com</text>
<line x1="825" y1="133" x2="1125" y2="133" stroke="rgba(255,255,255,0.10)"/>
</g>

{system_rows_html}

<g opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="3.34s" fill="freeze"/>
<text x="470" y="577" font-size="14" fill="#94A3B8">&#9656; More about me &amp; projects below in README &#8595; <tspan fill="{label_color}">&#9608;<animate attributeName="fill-opacity" values="1;0;1" dur="1s" repeatCount="indefinite"/></tspan></text>
</g>
</g>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="3" opacity="0.55" filter="url(#glow8)"/>
<rect x="3" y="3" width="1174" height="604" rx="17" fill="none" stroke="url(#accent)" stroke-width="1.6"/>
</svg>"""
    return svg_content


def main():
    print("Generating dark.svg...")
    dark_svg = generate_svg(is_dark_mode=True)
    with open(DARK_SVG_PATH, "w") as f:
        f.write(dark_svg)
    print(f"Wrote {DARK_SVG_PATH} ({len(dark_svg)} bytes)")

    print("Generating light.svg...")
    light_svg = generate_svg(is_dark_mode=False)
    with open(LIGHT_SVG_PATH, "w") as f:
        f.write(light_svg)
    print(f"Wrote {LIGHT_SVG_PATH} ({len(light_svg)} bytes)")


if __name__ == "__main__":
    main()
