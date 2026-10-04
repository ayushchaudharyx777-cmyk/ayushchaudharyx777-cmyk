"""Builds contribution-graph.svg (last 31 days) from the public GitHub contributions page."""
import re, sys, datetime, urllib.request
USER = "ayushchaudharyx777-cmyk"
DAYS = 31
def fetch():
    req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                                 headers={"X-Requested-With": "XMLHttpRequest", "User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf8")
def parse(html):
    ids = dict((i, d) for d, i in re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*?id="(contribution-day-component-[\d-]+)"', html))
    out = {}
    for cid, tip in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)', html):
        if cid in ids:
            m = re.match(r"\s*(\d+) contribution", tip)
            out[ids[cid]] = int(m.group(1)) if m else 0
    return sorted(out.items())
def build(data):
    today = datetime.date.today().isoformat()
    data = [(d, c) for d, c in data if d <= today][-DAYS:]
    W, H, L, R, T, B = 1000, 320, 60, 30, 70, 50
    mx = max(max(c for _, c in data), 4)
    step = max(1, -(-mx // 4)); top = step * 4
    X = lambda i: L + i * (W - L - R) / (len(data) - 1)
    Y = lambda v: H - B - v * (H - T - B) / top
    pts = [(X(i), Y(c)) for i, (_, c) in enumerate(data)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{L},{H-B} " + line + f" {W-R},{H-B}"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">',
         '<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#39D353" stop-opacity="0.55"/><stop offset="1" stop-color="#39D353" stop-opacity="0.03"/></linearGradient>',
         '<linearGradient id="l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8B5CF6"/><stop offset="0.5" stop-color="#00C8FF"/><stop offset="1" stop-color="#39D353"/></linearGradient></defs>',
         f'<rect width="{W}" height="{H}" rx="14" fill="#0D1117"/>',
         f'<text x="{W/2}" y="36" text-anchor="middle" fill="#FFFFFF" font-size="20" font-weight="600">Ayush Chaudhary\'s Contribution Graph</text>',
         f'<text x="{W/2}" y="56" text-anchor="middle" fill="#8B949E" font-size="12">last {len(data)} days &#183; {sum(c for _, c in data)} contributions</text>']
    for k in range(5):
        v = step * k; y = Y(v)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#FFFFFF" stroke-opacity="0.08"/>')
        s.append(f'<text x="{L-10}" y="{y+4:.1f}" text-anchor="end" fill="#8B949E" font-size="12">{v}</text>')
    for i, (d, _) in enumerate(data):
        if i % 3 == 0 or i == len(data) - 1:
            dt = datetime.date.fromisoformat(d)
            s.append(f'<text x="{X(i):.1f}" y="{H-B+20}" text-anchor="middle" fill="#8B949E" font-size="11">{dt.day} {dt.strftime("%b")}</text>')
    s.append(f'<polygon points="{area}" fill="url(#a)"/>')
    s.append(f'<polyline points="{line}" fill="none" stroke="url(#l)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    for (x, y), (_, c) in zip(pts, data):
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.5 if c else 2.5}" fill="#FFFFFF" fill-opacity="{1 if c else 0.5}"/>')
    s.append("</svg>")
    return "\n".join(s)
if __name__ == "__main__":
    html = open(sys.argv[1], encoding="utf8").read() if len(sys.argv) > 1 else fetch()
    data = parse(html)
    if len(data) < DAYS: sys.exit("could not read contributions")
    open("contribution-graph.svg", "w", encoding="utf8").write(build(data))
    print("ok", data[-3:])
