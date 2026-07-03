# -*- coding: utf-8 -*-
# Renders TheClazer's contribution calendar as a custom purple grid SVG.
# Uses GH_TOKEN (a user PAT includes PRIVATE contributions; the default
# GITHUB_TOKEN sees PUBLIC only).
import os, json, datetime, urllib.request

TOKEN = os.environ["GH_TOKEN"]
USER = "TheClazer"
query = 'query { user(login: "%s") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount weekday } } } } } }' % USER
body = json.dumps({"query": query}).encode()
req = urllib.request.Request(
    "https://api.github.com/graphql", data=body,
    headers={"Authorization": "bearer " + TOKEN, "Content-Type": "application/json", "User-Agent": "contrib-grid"})
cal = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks = cal["weeks"]; total = cal["totalContributions"]
active = sum(1 for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)

COLORS = ["#221f33", "#3a2e63", "#5b46a8", "#8a63e0", "#bb9af7"]
def lvl(c):
    if c <= 0: return 0
    if c <= 2: return 1
    if c <= 6: return 2
    if c <= 14: return 3
    return 4

STEP = 14; CELL = 11; GX = 36; GY = 40
W = GX + len(weeks) * STEP + 16
H = GY + 7 * STEP + 38
MUTED = "#8b8fa3"; FRAME = "#3a2e63"; BG = "#1a1b27"; BRIGHT = "#d4bbff"

o = []
o.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="Segoe UI, Verdana, sans-serif">' % (W, H, W, H))
o.append('<rect x="0" y="0" width="%d" height="%d" rx="14" fill="%s"/>' % (W, H, BG))
o.append('<rect x="1.5" y="1.5" width="%d" height="%d" rx="13" fill="none" stroke="%s" stroke-width="1.5"/>' % (W-3, H-3, FRAME))
o.append('<text x="%d" y="24" fill="%s" font-size="12" font-weight="600" letter-spacing="2">CONTRIBUTIONS</text>' % (GX, MUTED))
last = None
for wi, w in enumerate(weeks):
    m = datetime.datetime.strptime(w["contributionDays"][0]["date"], "%Y-%m-%d").strftime("%b")
    if m != last:
        o.append('<text x="%d" y="%d" fill="%s" font-size="9">%s</text>' % (GX + wi*STEP, GY-6, MUTED, m)); last = m
for wd, lab in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
    o.append('<text x="6" y="%d" fill="%s" font-size="9">%s</text>' % (GY + wd*STEP + CELL-1, MUTED, lab))
for wi, w in enumerate(weeks):
    for d in w["contributionDays"]:
        o.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2.5" fill="%s"/>' % (GX + wi*STEP, GY + d["weekday"]*STEP, CELL, CELL, COLORS[lvl(d["contributionCount"])]))
by = H - 14
o.append('<text x="%d" y="%d" fill="%s" font-size="10"><tspan fill="%s" font-weight="700">%d</tspan> contributions · %d active days</text>' % (GX, by, MUTED, BRIGHT, total, active))
lx = W - 16 - (5*14 + 70)
o.append('<text x="%d" y="%d" fill="%s" font-size="9">Less</text>' % (lx, by, MUTED))
for i, col in enumerate(COLORS):
    o.append('<rect x="%d" y="%d" width="11" height="11" rx="2.5" fill="%s"/>' % (lx + 26 + i*14, by-9, col))
o.append('<text x="%d" y="%d" fill="%s" font-size="9">More</text>' % (lx + 26 + 5*14 + 4, by, MUTED))
o.append('</svg>')
open("contribution-grid.svg", "w", encoding="utf-8", newline="\n").write("\n".join(o))
print("rendered %dx%d total=%d active=%d" % (W, H, total, active))
