"""Real brand logos for the logo-link effect.

The bundled set (assets/logos.json) comes from Simple Icons (simpleicons.org, CC0 1.0); the logos themselves
are trademarks of their owners. This file draws their SVG paths with a tiny rasteriser, so nothing extra
needs installing. Brands that are not in the set can be passed as your own PNG/JPG file instead.
"""
import json, math, os, re

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NUM = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')
ALIAS = {'gemini': 'googlegemini', 'chrome': 'googlechrome', 'drive': 'googledrive', 'sheets': 'googlesheets',
         'docs': 'googledocs', 'calendar': 'googlecalendar', 'meet': 'googlemeet', 'mistral': 'mistralai',
         'hf': 'huggingface', 'twitter': 'x', 'firefox': 'firefoxbrowser', 'claudecode': 'claude', 'claudeai': 'claude',
         'gcp': 'googlecloud', 'node': 'nodedotjs', 'nodejs': 'nodedotjs', 'next': 'nextdotjs', 'nextjs': 'nextdotjs',
         'tailwind': 'tailwindcss', 'postgres': 'postgresql', 'davinci': 'davinciresolve', 'resolve': 'davinciresolve',
         'colab': 'googlecolab', 'ig': 'instagram', 'insta': 'instagram', 'yt': 'youtube', 'fb': 'facebook',
         'wa': 'whatsapp', 'gh': 'github', 'metaai': 'meta', 'llama': 'meta', 'elevenlabsio': 'elevenlabs'}
_DATA = None


def data():
    global _DATA
    if _DATA is None:
        try: _DATA = json.load(open(os.path.join(ROOT, 'assets', 'logos.json')))['icons']
        except Exception: _DATA = {}
    return _DATA


def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower().replace('+', 'plus').replace('.', 'dot'))


def find(name):
    """Look a brand up by slug, title or alias. Returns (slug, entry) or (None, None)."""
    icons = data(); k = norm(name)
    k2 = re.sub(r'[^a-z0-9]', '', name.lower())
    for key in (k, k2, ALIAS.get(k), ALIAS.get(k2)):
        if key and key in icons: return key, icons[key]
    for slug, v in icons.items():
        if norm(v['title']) in (k, k2) or any(norm(a) in (k, k2) for a in v.get('aka', [])): return slug, v
    return None, None


class _Scan:
    def __init__(self, d): self.d, self.i = d, 0
    def skip(self):
        while self.i < len(self.d) and self.d[self.i] in ' ,\t\n\r': self.i += 1
    def cmd(self):
        self.skip()
        if self.i < len(self.d) and self.d[self.i].isalpha():
            self.i += 1; return self.d[self.i - 1]
        return None
    def more(self):
        self.skip(); return self.i < len(self.d) and not self.d[self.i].isalpha()
    def num(self):
        self.skip(); m = _NUM.match(self.d, self.i)
        if not m: raise ValueError(f'bad path data at {self.i}')
        self.i = m.end(); return float(m.group())
    def flag(self):
        self.skip(); ch = self.d[self.i]; self.i += 1; return ch == '1'


def _arc(x1, y1, rx, ry, phi, fa, fs, x2, y2):
    if rx == 0 or ry == 0 or (x1 == x2 and y1 == y2): return [(x2, y2)]
    cp, sp = math.cos(math.radians(phi)), math.sin(math.radians(phi))
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = cp * dx + sp * dy, -sp * dx + cp * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1: s = math.sqrt(lam); rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if fa == fs: co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx, cy = cp * cxp - sp * cyp + (x1 + x2) / 2, sp * cxp + cp * cyp + (y1 + y2) / 2
    ang = lambda ux, uy, vx, vy: math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0: dt -= 2 * math.pi
    elif fs and dt < 0: dt += 2 * math.pi
    n = max(4, int(abs(dt) / (math.pi / 16)))
    return [(cp * rx * math.cos(t1 + dt * i / n) - sp * ry * math.sin(t1 + dt * i / n) + cx,
             sp * rx * math.cos(t1 + dt * i / n) + cp * ry * math.sin(t1 + dt * i / n) + cy) for i in range(1, n + 1)]


def polygons(d, steps=14):
    """Flatten SVG path data into closed polygons (lists of points)."""
    s = _Scan(d); polys, cur = [], []
    x = y = sx = sy = 0.0; cx2 = cy2 = None; last = ''
    def bez(p, n=steps):
        out = []
        for i in range(1, n + 1):
            t = i / n; u = 1 - t
            if len(p) == 4:
                out.append((u ** 3 * p[0][0] + 3 * u * u * t * p[1][0] + 3 * u * t * t * p[2][0] + t ** 3 * p[3][0],
                            u ** 3 * p[0][1] + 3 * u * u * t * p[1][1] + 3 * u * t * t * p[2][1] + t ** 3 * p[3][1]))
            else:
                out.append((u * u * p[0][0] + 2 * u * t * p[1][0] + t * t * p[2][0], u * u * p[0][1] + 2 * u * t * p[1][1] + t * t * p[2][1]))
        return out
    cmd = None
    while True:
        c = s.cmd()
        if c is None:
            if cmd is None or not s.more(): break
            c = {'M': 'L', 'm': 'l'}.get(cmd, cmd)
        cmd = c; rel = c.islower(); C = c.upper()
        if C == 'Z':
            if cur: polys.append(cur); cur = []
            x, y = sx, sy; last = 'Z'; continue
        first = True
        while first or s.more():
            first = False
            ox, oy = (x, y) if rel else (0.0, 0.0)
            if C == 'M':
                x, y = s.num() + ox, s.num() + oy
                if cur: polys.append(cur)
                cur = [(x, y)]; sx, sy = x, y; C = 'L'; cmd = 'l' if rel else 'L'; last = 'M'; continue
            if not cur: cur = [(x, y)]
            if C == 'L': x, y = s.num() + ox, s.num() + oy; cur.append((x, y))
            elif C == 'H': x = s.num() + ox; cur.append((x, y))
            elif C == 'V': y = s.num() + oy; cur.append((x, y))
            elif C in 'CS':
                if C == 'C': x1, y1 = s.num() + ox, s.num() + oy
                else: x1, y1 = (2 * x - cx2, 2 * y - cy2) if last in 'CS' and cx2 is not None else (x, y)
                x2_, y2_ = s.num() + ox, s.num() + oy; ex, ey = s.num() + ox, s.num() + oy
                cur += bez([(x, y), (x1, y1), (x2_, y2_), (ex, ey)]); cx2, cy2 = x2_, y2_; x, y = ex, ey
            elif C in 'QT':
                if C == 'Q': x1, y1 = s.num() + ox, s.num() + oy
                else: x1, y1 = (2 * x - cx2, 2 * y - cy2) if last in 'QT' and cx2 is not None else (x, y)
                ex, ey = s.num() + ox, s.num() + oy
                cur += bez([(x, y), (x1, y1), (ex, ey)]); cx2, cy2 = x1, y1; x, y = ex, ey
            elif C == 'A':
                rx, ry, phi = s.num(), s.num(), s.num(); fa, fs = s.flag(), s.flag()
                ex, ey = s.num() + ox, s.num() + oy
                cur += _arc(x, y, rx, ry, phi, fa, fs, ex, ey); x, y = ex, ey
            last = C
    if cur: polys.append(cur)
    return polys


def raster(polys, size, ss=4, view=24.0):
    """Fill polygons with the SVG non-zero rule into an anti-aliased size x size mask."""
    S = size * ss; sc = S / view; edges = []
    for p in polys:
        q = p + [p[0]]
        for (x0, y0), (x1, y1) in zip(q[:-1], q[1:]):
            if y0 != y1: edges.append((x0 * sc, y0 * sc, x1 * sc, y1 * sc))
    img = np.zeros((S, S), np.uint8)
    if edges:
        x0, y0, x1, y1 = np.array(edges, np.float64).T
        wind = np.where(y1 > y0, 1, -1); ymin, ymax = np.minimum(y0, y1), np.maximum(y0, y1)
        for row in range(S):
            yc = row + 0.5; act = (ymin <= yc) & (ymax > yc)
            if not act.any(): continue
            xi = x0[act] + (yc - y0[act]) * (x1[act] - x0[act]) / (y1[act] - y0[act])
            o = np.argsort(xi); xi = xi[o]; cw = np.cumsum(wind[act][o])
            for k in np.nonzero(cw[:-1] != 0)[0]:
                a, b = int(math.ceil(xi[k] - 0.5)), int(math.floor(xi[k + 1] - 0.5))
                if b >= a: img[row, max(0, a):min(S, b + 1)] = 255
    return Image.fromarray(img).resize((size, size), Image.BOX)


def hex_rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def logo_image(name, size, color=None):
    """RGBA logo of `name` (a brand name, or a path to your own PNG/JPG), or None if unknown."""
    if os.path.exists(name):
        im = Image.open(name).convert('RGBA'); s = size / max(im.size)
        return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    slug, v = find(name)
    if not v: return None
    mask = raster(polygons(v['path']), size)
    im = Image.new('RGBA', (size, size), (color or hex_rgb(v['hex'])) + (255,)); im.putalpha(mask)
    return im


def brand_color(name):
    slug, v = find(name) if name else (None, None)
    return hex_rgb(v['hex']) if v else None


def title(name):
    slug, v = find(name)
    return v['title'] if v else name


if __name__ == '__main__':
    icons = data()
    print(f'{len(icons)} bundled logos:')
    print(', '.join(sorted(v['title'] for v in icons.values())))
