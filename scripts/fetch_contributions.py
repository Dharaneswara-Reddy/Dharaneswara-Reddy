#!/usr/bin/env python3
"""
Scrape real daily contribution counts from GitHub's public contributions
endpoint and write data/contributions.json with raw days plus derived stats.
No token, no auth, no GraphQL -- just the public HTML GitHub already serves.
"""
import datetime, json, os, re, sys
import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_PROFILE_USER", "Dharaneswara-Reddy")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")

def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot/1.0"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        print("no calendar cells found", file=sys.stderr); sys.exit(1)
    days = []
    for td in cells:
        date = td.get("data-date")
        if not date: continue
        td_id = td.get("id")
        tip = soup.find("tool-tip", attrs={"for": td_id}) if td_id else None
        text = tip.get_text(strip=True) if tip else ""
        if re.search(r"no contributions", text, re.I): count = 0
        else:
            m = re.match(r"(\d+)", text)
            count = int(m.group(1)) if m else 0
        days.append({"date": date, "count": count})
    days.sort(key=lambda d: d["date"])
    return days

def compute_current_streak(days):
    idx = len(days) - 1
    if days[idx]["count"] == 0: idx -= 1
    streak, end_idx = 0, idx
    while idx >= 0 and days[idx]["count"] > 0: streak += 1; idx -= 1
    if streak == 0: return 0, None, None
    return streak, days[idx+1]["date"], days[end_idx]["date"]

def compute_longest_streak(days):
    longest = run = 0; ls = le = None; rsi = None
    for i, d in enumerate(days):
        if d["count"] > 0:
            if run == 0: rsi = i
            run += 1
            if run > longest: longest, ls, le = run, days[rsi]["date"], days[i]["date"]
        else: run = 0
    return longest, ls, le

def build_data(days):
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"] > 0)
    best = max(days, key=lambda d: d["count"])
    cl, cs, ce = compute_current_streak(days)
    ll, ls, le = compute_longest_streak(days)
    monthly = {}
    for d in days: k = d["date"][:7]; monthly[k] = monthly.get(k, 0) + d["count"]
    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total, "active_days": active,
        "avg_per_active_day": round(total / active, 1) if active else 0,
        "current_streak": {"length": cl, "start": cs, "end": ce},
        "longest_streak": {"length": ll, "start": ls, "end": le},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": [{"month": k, "total": v} for k, v in sorted(monthly.items())],
        "days": days,
    }

if __name__ == "__main__":
    days = fetch_days()
    data = build_data(days)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f: json.dump(data, f, indent=2)
    print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions, "
          f"streak {data['current_streak']['length']}, longest {data['longest_streak']['length']}")
