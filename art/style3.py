"""Clean 'ligne claire' style: uniform confident outlines, flat tones, crisp shadow shapes."""
import math, random
import lib
from lib import C, G, ell, bez, rrect, resample
import palette as P
from reportlab.lib.colors import white, black

# ------------------------------------------------------------------ scale-aware transforms
_SC = [1.0]
class T:
    def __init__(self, x, y, s=1.0, flip=False, rot=0):
        self.a = (x, y, s, flip, rot)
    def __enter__(self):
        x, y, s, flip, rot = self.a
        C.saveState(); C.translate(x, y); C.rotate(rot); C.scale(-s if flip else s, s)
        _SC.append(_SC[-1]*s)
    def __exit__(self, *e):
        _SC.pop(); C.restoreState()

def poly(pts, closed=True):
    p = C.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

# ------------------------------------------------------------------ primitives
LINE = 1.15   # page-space outline weight for characters (pt)

_R = random.Random(21)
def _noise(n, amp, freqs=((1.0, 0.7), (2.6, 0.3)), step_pt=1.1, period_pt=45.0):
    ph = [_R.random()*6.28 for _ in freqs]
    return [amp*sum(a*math.sin((t*step_pt/period_pt)*f*6.28 + p) for (f, a), p in zip(freqs, ph)) for t in range(n)]

HAND = True
def stroke(pts, w=LINE, closed=False, g=0.0, alpha=None, taper=True):
    """hand-inked stroke: gentle wobble, pressure variation, tapered ends, overlapping closures"""
    sc = _SC[-1]
    if not HAND:
        C.saveState(); C.setStrokeColor(G(g)); C.setLineWidth(w/sc); C.setLineCap(1); C.setLineJoin(1)
        C.drawPath(poly(pts, closed), fill=0, stroke=1); C.restoreState(); return
    P = resample(list(pts), 1.1/sc, closed)
    if len(P) < 3:
        P = resample(list(pts), 0.3/sc, closed)
        if len(P) < 2: return
    if closed:
        k = _R.randrange(len(P))
        P = P[k:] + P[:k]
        ov = max(2, int(len(P)*0.05))
        P = P + P[:ov]
    n = len(P)
    wob = _noise(n, 0.3/sc)
    prs = _noise(n, 0.28, ((1.4, 0.7), (3.3, 0.3)), period_pt=30.0)
    left, right = [], []
    for i in range(n):
        a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy/L, dx/L
        t = i/(n-1)
        px, py = P[i][0]+nx*wob[i], P[i][1]+ny*wob[i]
        if taper or closed:
            tp = min(1.0, t/0.12, (1-t)/0.12) if n > 8 else 1.0
            tp = 0.25 + 0.75*math.sin(tp*math.pi/2)
        else:
            tp = 1.0
        ww = (w/sc)*tp*(1.0+prs[i])/2
        left.append((px+nx*ww, py+ny*ww)); right.append((px-nx*ww, py-ny*ww))
    alpha = lib.alpha_for(g, alpha)
    C.saveState(); C.setFillColor(G(g))
    if alpha is not None: C.setFillAlpha(alpha)
    C.drawPath(poly(left + list(reversed(right))), fill=1, stroke=0); C.restoreState()

def hatch(clip, spacing=1.6, ang=45, lw=0.45, g=0.0, alpha=0.85, wob=True):
    """hand hatching inside clip (spacing, lw in page pt)"""
    sc = _SC[-1]
    x0, y0, x1, y1 = bbox(clip)
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    L = math.hypot(x1-x0, y1-y0)
    cx, cy = (x0+x1)/2, (y0+y1)/2
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    k = -L/2; i = 0
    while k < L/2:
        ox, oy = cx - dy*k, cy + dx*k
        j = (_R.random()-0.5)*spacing/sc*0.4
        stroke([(ox-dx*L/2+j, oy-dy*L/2), (ox+dx*L/2, oy+dy*L/2+j)], lw, g=g, alpha=alpha)
        k += spacing/sc; i += 1
    C.restoreState()

def fill(pts, g, alpha=None):
    alpha = lib.alpha_for(g, alpha)
    C.saveState(); C.setFillColor(G(g))
    if alpha is not None: C.setFillAlpha(alpha)
    C.drawPath(poly(pts), fill=1, stroke=0); C.restoreState()

def shape(pts, g, w=LINE, shadow=None):
    """flat fill; optional crisp shadow shape clipped inside; outline"""
    if HAND and g < 0.98:
        sc = _SC[-1]; ox, oy = 0.28/sc, -0.22/sc
        fill([(x+ox, y+oy) for x, y in pts], g)
    else:
        fill(pts, g)
    if shadow is not None:
        sh_pts, sh_g = shadow
        C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0); fill(sh_pts, sh_g); C.restoreState()
    if w: stroke(pts, w, closed=True)

def clip_fill(clip, pts, g, alpha=None):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0); fill(pts, g, alpha); C.restoreState()

def offset_shadow(pts, dx, dy, g_delta=0.12, base=None):
    """crisp shadow: part of shape NOT covered by a shifted copy"""
    x0, y0, x1, y1 = bbox(pts)
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    p = C.beginPath(); p.rect(x0-100, y0-100, x1-x0+200, y1-y0+200)
    sh = [(x+dx, y+dy) for x, y in pts]
    p.moveTo(*sh[0])
    for q in sh[1:]: p.lineTo(*q)
    p.close()
    C.setFillColor(black); C.setFillAlpha(g_delta)
    C.drawPath(p, fill=1, stroke=0, fillMode=0); C.restoreState()

def form(pts, g, w=LINE, sdx=-1.4, sdy=1.2, sh=0.13):
    if HAND and g < 0.98:
        sc = _SC[-1]; fill([(x+0.28/sc, y-0.22/sc) for x, y in pts], g)
    else:
        fill(pts, g)
    if sh: offset_shadow(pts, sdx, sdy, sh)
    if w: stroke(pts, w, closed=True)

def dot(x, y, r, g=0.0):
    C.saveState(); C.setFillColor(G(g)); C.circle(x, y, r, fill=1, stroke=0); C.restoreState()

def cast_shadow(x, y, rx, ry, g=0.0, a=0.16):
    e = ell(x, y, rx, ry, 30)
    fill(e, 0.0, 0.07)
    hatch(e, 1.5, 20, 0.45, 0.0, 0.6)

def tube(pts, w0, w1, g, lw=LINE, cap=True, sh=0.12):
    P = resample(pts, 0.6)
    n = len(P); left, right = [], []
    for i in range(n):
        a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        w = (w0 + (w1-w0)*i/(n-1))/2
        left.append((P[i][0]-dy/L*w, P[i][1]+dx/L*w)); right.append((P[i][0]+dy/L*w, P[i][1]-dx/L*w))
    a2 = math.degrees(math.atan2(P[-1][1]-P[-2][1], P[-1][0]-P[-2][0]))
    a1 = math.degrees(math.atan2(P[1][1]-P[0][1], P[1][0]-P[0][0]))
    cap1 = ell(P[-1][0], P[-1][1], w1/2, w1/2, 10, a2-90, a2+90)
    cap0 = ell(P[0][0], P[0][1], w0/2, w0/2, 10, a1+90, a1+270)
    outline = left + cap1 + list(reversed(right)) + cap0
    fill(outline, g)
    if sh: offset_shadow(outline, -w0*0.3, w0*0.12, sh)
    stroke(left, lw); stroke(right, lw)
    if cap: stroke(cap1, lw)
    return outline

# ------------------------------------------------------------------ hands, props
def hand(x, y, ang, r=2.2):
    with T(x, y, 1, rot=ang+90):
        palm = bez((-r*0.8, r*0.3), (-r, -r*0.8), (-r*0.8, -r*1.9), (0, -r*2.0)) + bez((0, -r*2.0), (r*0.8, -r*1.9), (r, -r*0.8), (r*0.8, r*0.3))
        shape(palm, P.SKIN, LINE*0.9)
        stroke(bez((r*0.75, -r*0.2), (r*1.5, -r*0.3), (r*1.6, -r*1.1), (r*1.0, -r*1.3)), LINE*0.8)

def magnifier(x, y, ang=35, r=5.0):
    with T(x, y, rot=ang):
        tube([(0, -r-0.6), (0, -r-9.5)], 2.3, 2.1, P.MAGNIFIER_HANDLE)
        shape(ell(0, 0, r+1.2, r+1.2, 40), P.MAGNIFIER_RIM)
        shape(ell(0, 0, r, r, 40), P.GLASS)
        stroke(ell(0, 0, r*0.68, r*0.68, 16, 110, 165), LINE*1.3, g=1.0)

def notebook(x, y, s=1.0, drawing=False):
    with T(x, y, s):
        shape(rrect(-7.5, -5.4, 15, 10.8, 1), P.NOTEBOOK_COVER)
        for side in (-1, 1):
            pg = rrect(-7 if side < 0 else 0.2, -4.7, 6.8, 9.5, 0.5)
            shape(pg, 1.0, LINE*0.6)
            if drawing and side > 0:
                stroke(ell(3.6, 0, 1.8, 1.8, 14), LINE*0.5, closed=True)
                for a in range(0, 360, 60):
                    stroke([(3.6+math.cos(math.radians(a))*2.3, math.sin(math.radians(a))*2.3),
                            (3.6+math.cos(math.radians(a))*3.0, math.sin(math.radians(a))*3.0)], LINE*0.4)
            else:
                for k in range(4):
                    xo = -6.2 if side < 0 else 1.0
                    stroke([(xo, 2.6-k*2.0), (xo+5.2, 2.6-k*2.0)], LINE*0.3, g=P.NOTEBOOK_LINE)

def bunny(x, y, s=1.0):
    """Hanka's plush bunny"""
    with T(x, y, s):
        for sx in (-1, 1):
            ear = bez((sx*1.2, 6.5), (sx*1.8, 11), (sx*3.4, 14.5), (sx*4, 13.5)) + bez((sx*4, 13.5), (sx*4.6, 12), (sx*3.4, 8), (sx*2.8, 6))
            shape(ear, 0.92, LINE*0.8)
            fill(bez((sx*2, 7.5), (sx*2.5, 10.5), (sx*3.4, 12.5), (sx*3.7, 12.6)) + [(sx*3.1, 8)], 0.75)
        shape(ell(0, -1, 4.2, 5, 24), 0.92, LINE*0.8)
        shape(ell(0, 4.2, 4, 3.6, 24), 0.92, LINE*0.8)
        dot(-1.4, 4.6, 0.5); dot(1.4, 4.6, 0.5)
        dot(0, 3.4, 0.45, 0.3)
        shape(ell(0, -1.5, 2.2, 2.6, 16), 1.0, LINE*0.5)
        for sx in (-1, 1): shape(ell(sx*2.6, -5.2, 1.6, 1.1, 12), 0.92, LINE*0.7)

# ------------------------------------------------------------------ faces
def face(cx, cy, r, mood="happy", look=(0, 0), young=False, freckles=False):
    ex = r*0.40 if not young else r*0.42
    ey = cy - r*0.02 if not young else cy - r*0.12
    erx, ery = r*0.095, r*0.135
    if young: erx, ery = r*0.105, r*0.14
    lx, ly = look[0]*r*0.04, look[1]*r*0.03
    for s in (-1, 1):
        x = cx + s*ex
        if mood in ("closed", "sleepy"):
            stroke(bez((x-erx*1.4, ey), (x-erx*0.5, ey-ery*0.8), (x+erx*0.5, ey-ery*0.8), (x+erx*1.4, ey)), LINE*0.9)
            continue
        k = 1.25 if mood in ("surprised", "wow") else 1.0
        if mood in ("grin", "laugh"):
            stroke(bez((x-erx*1.4, ey-ery*0.3), (x-erx*0.6, ey+ery*0.9), (x+erx*0.6, ey+ery*0.9), (x+erx*1.4, ey-ery*0.3)), LINE*1.2)
            continue
        C.saveState(); C.setFillColor(black)
        C.ellipse(x+lx-erx*k, ey+ly-ery*k, x+lx+erx*k, ey+ly+ery*k, fill=1, stroke=0); C.restoreState()
        dot(x+lx+erx*0.35, ey+ly+ery*0.4, erx*0.38, 1.0)
    # brows
    by = ey + r*(0.32 if not young else 0.3)
    bw = r*0.17
    for s in (-1, 1):
        x = cx + s*ex
        if mood in ("surprised", "wow"):
            pts = bez((x-bw, by+r*0.06), (x-bw*0.3, by+r*0.14), (x+bw*0.3, by+r*0.14), (x+bw, by+r*0.06))
        elif mood == "determined":
            pts = [(x-s*bw, by+r*0.05), (x+s*bw, by-r*0.03)]
        elif mood in ("worried", "sad", "think"):
            pts = [(x-s*bw, by-r*0.02), (x+s*bw, by+r*0.07)]
        else:
            pts = bez((x-bw, by), (x-bw*0.3, by+r*0.06), (x+bw*0.3, by+r*0.06), (x+bw, by))
        stroke(pts, LINE*0.85)
    # nose
    ny = ey - r*(0.3 if not young else 0.26)
    if young:
        stroke(bez((cx-r*0.07, ny+r*0.02), (cx-r*0.02, ny-r*0.05), (cx+r*0.05, ny-r*0.05), (cx+r*0.09, ny+r*0.02)), LINE*0.75)
    else:
        stroke(bez((cx+r*0.05, ey-r*0.1), (cx+r*0.12, ny), (cx+r*0.06, ny-r*0.06), (cx-r*0.05, ny-r*0.04)), LINE*0.75)
    # mouth
    my = ey - r*(0.52 if not young else 0.48)
    mw = r*0.2
    if mood in ("happy", "determined", "calm"):
        stroke(bez((cx-mw, my+r*0.03), (cx-mw*0.4, my-r*0.07), (cx+mw*0.4, my-r*0.07), (cx+mw, my+r*0.03)), LINE*0.85)
    elif mood in ("grin", "laugh"):
        m = bez((cx-mw*1.2, my+r*0.04), (cx-mw*0.6, my-r*0.24), (cx+mw*0.6, my-r*0.24), (cx+mw*1.2, my+r*0.04)) + [(cx-mw*1.2, my+r*0.04)]
        shape(m, P.MOUTH, LINE*0.85)
        clip_fill(m, ell(cx, my-r*0.2, mw*0.6, r*0.08, 12), P.TONGUE)
    elif mood in ("surprised", "wow"):
        shape(ell(cx, my-r*0.04, r*0.08, r*0.11, 16), P.MOUTH, LINE*0.8)
    elif mood == "whisper":
        shape(ell(cx, my, r*0.05, r*0.06, 12), P.MOUTH, LINE*0.7)
    elif mood == "think":
        stroke(bez((cx-mw*0.6, my), (cx, my-r*0.02), (cx+mw*0.4, my+r*0.01), (cx+mw*0.8, my+r*0.05)), LINE*0.85)
    elif mood == "talk":
        shape(ell(cx, my-r*0.03, r*0.12, r*0.085, 16), P.MOUTH, LINE*0.8)
        clip_fill(ell(cx, my-r*0.03, r*0.12, r*0.085, 16), ell(cx, my-r*0.09, r*0.08, r*0.04, 12), P.TONGUE)
    elif mood in ("sad", "worried"):
        stroke(bez((cx-mw*0.8, my-r*0.04), (cx-mw*0.3, my+r*0.03), (cx+mw*0.3, my+r*0.03), (cx+mw*0.8, my-r*0.04)), LINE*0.85)
    else:
        stroke([(cx-mw*0.6, my), (cx+mw*0.6, my)], LINE*0.85)
    if young:
        for s in (-1, 1):
            fill(ell(cx+s*r*0.6, ey-r*0.33, r*0.16, r*0.1, 16), P.BLUSH, 0.07)
    if freckles:
        for s in (-1, 1):
            for dx, dy in ((-0.08, 0.02), (0.03, 0.06), (0.1, -0.02), (0.0, -0.05)):
                dot(cx+s*(r*0.52+dx*r), ey-r*0.25+dy*r, r*0.02, P.FRECKLE)

# ------------------------------------------------------------------ bodies
class Kid:
    """param set for a child figure (units: Alica height = 100)"""
    def __init__(self, young):
        self.young = young
        if young:   # Hanka, 4 years
            self.H = 80; self.hr = 9.6; self.hy = 70.2
            self.sh_y = 57.5; self.sh_w = 8.3; self.hip = 31; self.knee = 16; self.ankle = 4.5
            self.leg_w = (6.0, 4.6); self.arm_w = (5.2, 4.6); self.up = 11.5; self.fo = 11.5
        else:       # Alica, 7 years
            self.H = 100; self.hr = 9.8; self.hy = 89.8
            self.sh_y = 76; self.sh_w = 9.6; self.hip = 45; self.knee = 24; self.ankle = 5
            self.leg_w = (6.0, 4.4); self.arm_w = (5.4, 4.6); self.up = 15; self.fo = 14

POSES = {  # (upper arm angle, forearm angle) in degrees, measured from +x (right side arm; mirrored for left)
    "down":  (-80, -85),
    "wave":  (-10, 80),
    "up":    (70, 85),
    "lens":  (-55, 25),
    "point": (-15, 5),
    "hip":   (-60, -170),
    "front": (-75, 170),
    "chin":  (-75, 120),
    "hush":  (-72, 118),
    "hold":  (-60, -5),
    "hug":   (-80, 160),
    "back":  (-100, -110),
}

IK = {"chin": (3.0, -0.95), "hush": (1.2, -0.52), "cheek": (6.0, -0.5)}
def arm_pts(k, side, pose):
    if pose in IK:
        tx, ty = IK[pose]
        S = (side*k.sh_w, k.sh_y - 1.5); P = (side*tx, k.hy + ty*k.hr)
        a, b = k.up, k.fo
        dx, dy = P[0]-S[0], P[1]-S[1]; d = min(math.hypot(dx, dy), a+b-0.5); d = max(d, abs(a-b)+0.5)
        base = math.atan2(dy, dx); al = math.acos((a*a+d*d-b*b)/(2*a*d))
        best = None
        for sg in (-1, 1):
            E = (S[0]+math.cos(base+sg*al)*a, S[1]+math.sin(base+sg*al)*a)
            score = 0.3*side*E[0] - E[1]
            if best is None or score > best[0]: best = (score, E)
        E = best[1]
        fa = math.degrees(math.atan2(P[1]-E[1], P[0]-E[0]))
        Hh = (E[0]+math.cos(math.radians(fa))*b, E[1]+math.sin(math.radians(fa))*b)
        return S, E, Hh, fa
    ua, fa = POSES[pose]
    if side < 0: ua, fa = 180-ua, 180-fa
    sx, sy = side*k.sh_w, k.sh_y - 1.5
    ex, ey = sx + math.cos(math.radians(ua))*k.up, sy + math.sin(math.radians(ua))*k.up
    hx, hy = ex + math.cos(math.radians(fa))*k.fo, ey + math.sin(math.radians(fa))*k.fo
    return (sx, sy), (ex, ey), (hx, hy), fa

def draw_arm(k, side, pose, sleeve_g, cuff_g=None):
    s, e, h, fa = arm_pts(k, side, pose)
    tube([s, e], k.arm_w[0], k.arm_w[0]*0.95, sleeve_g)
    # forearm sleeve ends a bit before hand
    fx, fy = h[0]-math.cos(math.radians(fa))*2.2, h[1]-math.sin(math.radians(fa))*2.2
    tube([e, (fx, fy)], k.arm_w[0]*0.95, k.arm_w[1], sleeve_g)
    if cuff_g is not None:
        cx, cy = fx-math.cos(math.radians(fa))*1.0, fy-math.sin(math.radians(fa))*1.0
        tube([(cx, cy), (fx, fy)], k.arm_w[1]+0.4, k.arm_w[1]+0.4, cuff_g, sh=0)
    hand(h[0], h[1], fa, 2.1 if k.young else 2.3)
    return h, fa

def draw_legs(k, pose, leg_g, stripes=False, boots=0.3, boot_top=None):
    if pose == "walk":
        pts = [[(-3.8, k.hip), (-5.5, k.knee), (-9, k.ankle+1.5)], [(3.8, k.hip), (6.5, k.knee+0.5), (7.2, k.ankle)]]
    else:
        pts = [[(-3.8, k.hip), (-4.0, k.knee), (-4.2, k.ankle)], [(3.8, k.hip), (4.0, k.knee), (4.2, k.ankle)]]
    for leg in pts:
        o = tube(leg, k.leg_w[0], k.leg_w[1], leg_g)
        if stripes:
            C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
            for j in range(12):
                yy = k.ankle + j*3.4
                fill([(-20, yy), (20, yy), (20, yy+1.6), (-20, yy+1.6)], P.TIGHTS_STRIPE)
            C.restoreState()
            stroke(o, LINE, closed=True)
    bt = boot_top if boot_top is not None else k.ankle + (7 if not k.young else 5.5)
    for leg in pts:
        ax, ay = leg[-1]
        b = [(ax-3.0, bt), (ax+3.0, bt)] + bez((ax+3.0, bt), (ax+3.1, ay), (ax+3.5, 2.2), (ax+6.8, 2)) + \
            bez((ax+6.8, 2), (ax+7.6, 1.8), (ax+7.4, 0), (ax+6.5, 0)) + [(ax-3.2, 0)] + bez((ax-3.2, 0), (ax-3.6, 1), (ax-3.2, ay), (ax-3.0, bt))
        form(b, boots, sh=0.12)
        stroke([(ax-3.3, 1.3), (ax+7.1, 1.3)], LINE*0.7)
        stroke([(ax-3.0, bt-1.2), (ax+3.0, bt-1.2)], LINE*0.6)

def head_outline(k):
    r = k.hr; cy = k.hy
    if k.young:
        return bez((0, cy+r), (r*0.75, cy+r), (r*1.02, cy+r*0.45), (r*1.02, cy-r*0.05)) + \
               bez((r*1.02, cy-r*0.05), (r*1.02, cy-r*0.65), (r*0.6, cy-r*0.98), (0, cy-r*0.98)) + \
               bez((0, cy-r*0.98), (-r*0.6, cy-r*0.98), (-r*1.02, cy-r*0.65), (-r*1.02, cy-r*0.05)) + \
               bez((-r*1.02, cy-r*0.05), (-r*1.02, cy+r*0.45), (-r*0.75, cy+r), (0, cy+r))
    return bez((0, cy+r), (r*0.72, cy+r), (r*0.98, cy+r*0.5), (r*0.97, cy)) + \
           bez((r*0.97, cy), (r*0.95, cy-r*0.55), (r*0.6, cy-r*1.02), (0, cy-r*1.05)) + \
           bez((0, cy-r*1.05), (-r*0.6, cy-r*1.02), (-r*0.95, cy-r*0.55), (-r*0.97, cy)) + \
           bez((-r*0.97, cy), (-r*0.98, cy+r*0.5), (-r*0.72, cy+r), (0, cy+r))

# ---- ALICA hair
def alica_hair_back(k):
    r = k.hr; cy = k.hy
    back = bez((-r*0.98, cy+r*0.1), (-r*1.15, cy+r*1.15), (r*1.15, cy+r*1.15), (r*0.98, cy+r*0.1)) + \
           bez((r*0.98, cy+r*0.1), (r*1.25, cy-r*1.2), (r*1.35, cy-r*2.6), (r*1.3, cy-r*3.6)) + \
           [(r*0.9, cy-r*3.75), (r*0.5, cy-r*3.6), (-r*0.5, cy-r*3.6), (-r*0.9, cy-r*3.75), (-r*1.3, cy-r*3.6)] + \
           bez((-r*1.3, cy-r*3.6), (-r*1.35, cy-r*2.6), (-r*1.25, cy-r*1.2), (-r*0.98, cy+r*0.1))
    form(back, P.ALICA_HAIR, sh=0.0)

def alica_hair_front(k):
    r = k.hr; cy = k.hy
    for s in (-1, 1):
        lock = bez((s*r*0.55, cy+r*0.85), (s*r*1.05, cy+r*0.2), (s*r*1.2, cy-r*1.2), (s*r*1.28, cy-r*3.3)) + \
               [(s*r*1.1, cy-r*3.55), (s*r*0.82, cy-r*3.35)] + \
               bez((s*r*0.82, cy-r*3.35), (s*r*0.85, cy-r*2.0), (s*r*0.9, cy-r*0.9), (s*r*0.8, cy-r*0.2))
        shape(lock, P.ALICA_HAIR)
        stroke(bez((s*r*0.95, cy-r*0.4), (s*r*1.05, cy-r*1.4), (s*r*1.08, cy-r*2.4), (s*r*1.05, cy-r*3.2)), LINE*0.5, g=P.ALICA_HAIR_LINE)
    # crown with side part and swept fringe (soft points)
    cap = bez((-r*0.99, cy+r*0.0), (-r*1.08, cy+r*1.2), (-r*0.3, cy+r*1.28), (r*0.25, cy+r*1.2)) + \
          bez((r*0.25, cy+r*1.2), (r*0.9, cy+r*1.12), (r*1.1, cy+r*0.6), (r*0.99, cy+r*0.0)) + \
          bez((r*0.99, cy+r*0.0), (r*0.9, cy+r*0.3), (r*0.78, cy+r*0.42), (r*0.62, cy+r*0.46)) + \
          bez((r*0.62, cy+r*0.46), (r*0.5, cy+r*0.62), (r*0.35, cy+r*0.62), (r*0.22, cy+r*0.5)) + \
          bez((r*0.22, cy+r*0.5), (-r*0.1, cy+r*0.4), (-r*0.35, cy+r*0.36), (-r*0.52, cy+r*0.22)) + \
          bez((-r*0.52, cy+r*0.22), (-r*0.62, cy+r*0.35), (-r*0.8, cy+r*0.35), (-r*0.99, cy+r*0.0))
    shape(cap, P.ALICA_HAIR)
    # part line + flow lines
    stroke(bez((r*0.25, cy+r*1.2), (r*0.1, cy+r*1.0), (-r*0.1, cy+r*0.8), (-r*0.35, cy+r*0.55)), LINE*0.5, g=P.ALICA_HAIR_LINE)
    stroke(bez((-r*0.1, cy+r*1.18), (-r*0.5, cy+r*1.0), (-r*0.8, cy+r*0.7), (-r*0.92, cy+r*0.35)), LINE*0.5, g=P.ALICA_HAIR_LINE)
    stroke(bez((r*0.45, cy+r*1.12), (r*0.7, cy+r*0.95), (r*0.85, cy+r*0.7), (r*0.9, cy+r*0.4)), LINE*0.5, g=P.ALICA_HAIR_LINE)
    # shine
    stroke(bez((-r*0.55, cy+r*1.02), (-r*0.3, cy+r*1.12), (0, cy+r*1.14), (r*0.2, cy+r*1.1)), LINE*1.6, g=1.0, alpha=0.5)
    # clip (small bar)
    with T(r*0.62, cy+r*0.72, 1, rot=-20):
        shape(rrect(-2.2, -0.7, 4.4, 1.4, 0.6), P.ALICA_CLIP, LINE*0.8)

# ---- HANKA hair (curly, shoulder length)
def curl_outline(cx, cy, rx, ry, a0, a1, n, bump=0.22):
    pts = []
    for i in range(n):
        t0 = math.radians(a0 + (a1-a0)*i/n); t1 = math.radians(a0 + (a1-a0)*(i+1)/n)
        p0 = (cx+math.cos(t0)*rx, cy+math.sin(t0)*ry); p1 = (cx+math.cos(t1)*rx, cy+math.sin(t1)*ry)
        tm = (t0+t1)/2
        m = (cx+math.cos(tm)*rx*(1+bump), cy+math.sin(tm)*ry*(1+bump))
        pts += bez(p0, (p0[0]*0.5+m[0]*0.5+(m[0]-cx)*0.15, p0[1]*0.5+m[1]*0.5+(m[1]-cy)*0.15),
                   (p1[0]*0.5+m[0]*0.5+(m[0]-cx)*0.15, p1[1]*0.5+m[1]*0.5+(m[1]-cy)*0.15), p1, 5)
    return pts

HANKA_HAIR = P.HANKA_HAIR
def hanka_hair_back(k):
    r = k.hr; cy = k.hy
    back = curl_outline(0, cy-r*0.15, r*1.32, r*1.28, -30, 210, 13, 0.12) + \
           [(-r*1.1, cy-r*1.25), (-r*0.6, cy-r*1.45), (r*0.6, cy-r*1.45), (r*1.1, cy-r*1.25)]
    back = curl_outline(0, cy-r*0.15, r*1.32, r*1.28, -35, 215, 14, 0.12)
    # close bottom with curly edge
    x0, y0 = back[-1]; x1, y1 = back[0]
    bottom = curl_outline(0, cy-r*1.0, r*1.08, r*0.55, 215, 325, 5, 0.25)
    shape(back + bottom, HANKA_HAIR)
    for (a, rr) in ((200, 1.1), (230, 1.05), (310, 1.05), (340, 1.1)):
        x = math.cos(math.radians(a))*r*rr; y = cy-r*0.15+math.sin(math.radians(a))*r*rr
        stroke(ell(x, y, r*0.16, r*0.16, 10, 110, 220), LINE*0.4, g=P.HANKA_CURL)

def hanka_hair_front(k):
    r = k.hr; cy = k.hy
    top = curl_outline(0, cy+r*0.15, r*1.07, r*0.95, 5, 175, 9, 0.16)
    # fringe: small curls across forehead (right to left)
    fringe = []
    xs = [-r*1.05, -r*0.72, -r*0.38, 0, r*0.38, r*0.72, r*1.05]
    ys = [cy+r*0.15, cy+r*0.42, cy+r*0.5, cy+r*0.52, cy+r*0.5, cy+r*0.42, cy+r*0.15]
    for i in range(len(xs)-1):
        fringe += bez((xs[i], ys[i]), (xs[i]+r*0.05, ys[i]-r*0.2), (xs[i+1]-r*0.05, ys[i+1]-r*0.2), (xs[i+1], ys[i+1]), 5)
    shape(top + fringe, HANKA_HAIR)
    # side curls framing cheeks
    for s in (-1, 1):
        for (dx, dy, rr) in ((1.02, -0.05, 0.3), (1.08, -0.52, 0.28), (1.05, -0.95, 0.27)):
            c = curl_outline(s*r*dx, cy+r*dy, r*rr, r*rr, 0, 360, 6, 0.18)
            shape(c, HANKA_HAIR, LINE*0.9)
            stroke(ell(s*r*dx, cy+r*dy, r*rr*0.45, r*rr*0.45, 8, 110, 220), LINE*0.4, g=P.HANKA_CURL)
    for (dx, dy) in ((-0.5, 0.9), (0.1, 1.02), (0.6, 0.85), (-0.2, 0.72), (0.35, 0.7)):
        stroke(ell(r*dx, cy+r*dy, r*0.13, r*0.13, 8, 110, 220), LINE*0.4, g=P.HANKA_CURL)

# ------------------------------------------------------------------ figures
def alica(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0),
          lens=False, book=False, item=None, legs="stand", shadow=True):
    k = Kid(False)
    if shadow: cast_shadow(x, y, 15*s, 2.6*s)
    COAT = P.ALICA_COAT
    with T(x, y, s, flip):
        alica_hair_back(k)
        draw_legs(k, legs, P.TIGHTS, stripes=True, boots=P.ALICA_BOOTS)
        draw_arm(k, -1, left, COAT)
        # coat
        r = k.hr
        body = bez((-4.2, k.sh_y+2.8), (-7.5, k.sh_y+2.5), (-k.sh_w-1.2, k.sh_y+1), (-k.sh_w-1.6, k.sh_y-3)) + \
               bez((-k.sh_w-1.6, k.sh_y-3), (-11.5, 60), (-13, 50), (-14.2, 39)) + \
               bez((-14.2, 39), (-5, 37.2), (5, 37.2), (14.2, 39)) + \
               bez((14.2, 39), (13, 50), (11.5, 60), (k.sh_w+1.6, k.sh_y-3)) + \
               bez((k.sh_w+1.6, k.sh_y-3), (k.sh_w+1.2, k.sh_y+1), (7.5, k.sh_y+2.5), (4.2, k.sh_y+2.8)) + [(0, k.sh_y+0.5)]
        form(body, COAT, sdx=-2.2, sdy=1.2, sh=0.12)
        stroke([(0.5, k.sh_y+0.2), (0.9, 37.6)], LINE*0.8)
        for by in (70, 62, 54, 46):
            shape(ell(-1.8, by, 1.1, 1.1, 14), 1.0, LINE*0.7)
        for sx in (-1, 1):
            pk = [(sx*5, 47), (sx*11.3, 47), (sx*11.7, 41.5), (sx*5.3, 41.5)]
            stroke(pk, LINE*0.7, closed=True)
            stroke([(sx*5, 45.5), (sx*11.4, 45.5)], LINE*0.6)
        stroke(bez((-8, 58), (-7.5, 55), (-8.3, 52), (-8.8, 50)), LINE*0.5, g=P.ALICA_COAT_FOLD)
        stroke(bez((9, 42), (8.2, 40.8), (8.3, 39.5), (8.8, 38.3)), LINE*0.5, g=P.ALICA_COAT_FOLD)
        # collar
        for sx in (-1, 1):
            cl = [(sx*0.6, k.sh_y+0.2), (sx*4.5, k.sh_y+3.2), (sx*8.2, k.sh_y+0.8), (sx*3.5, k.sh_y-3.5)]
            shape(cl, P.ALICA_COLLAR, LINE*0.8)
        # satchel
        if not book:
            stroke(bez((7.8, k.sh_y+1.5), (2, 66), (-4, 55), (-10, 46)), LINE*2.2, g=0.0)
            stroke(bez((7.8, k.sh_y+1.5), (2, 66), (-4, 55), (-10, 46)), LINE*1.0, g=P.SATCHEL_STRAP)
            bag = rrect(-15, 39, 9.5, 8, 1.8)
            form(bag, P.SATCHEL)
            shape(bez((-15, 47), (-15, 43.5), (-5.5, 43.5), (-5.5, 47)) + [(-15, 47)], P.SATCHEL_FLAP, LINE*0.8)
            dot(-10.2, 44.3, 0.6, 0.95)
        h, fa = draw_arm(k, 1, right, COAT)
        if book:
            notebook(0, 57, 0.95); hand(h[0], h[1], fa); hand(-5, 55.5, -30)
        if lens:
            magnifier(h[0]+1.8, h[1]+7.5, ang=-20, r=4.8); hand(h[0], h[1], fa)
        if item: item(*h)
        # neck + head
        shape([(-2.6, k.sh_y+5), (2.6, k.sh_y+5), (2.8, k.sh_y+0.8), (-2.8, k.sh_y+0.8)], P.SKIN, 0)
        stroke([(-2.6, k.sh_y+5.5), (-2.8, k.sh_y+1)], LINE*0.8); stroke([(2.6, k.sh_y+5.5), (2.8, k.sh_y+1)], LINE*0.8)
        clip_fill([(-3, k.sh_y+5.5), (3, k.sh_y+5.5), (3, k.sh_y+0.8), (-3, k.sh_y+0.8)], ell(0, k.sh_y+5.5, 4, 2.5, 16), P.SKIN_SHADE)
        ho = head_outline(k)
        shape(ho, P.SKIN)
        face(0, k.hy, k.hr, mood, look, young=False, freckles=True)
        alica_hair_front(k)

def hanka(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0),
          bunny_toy=False, book=False, item=None, legs="stand", shadow=True, monkey=True, torch=False):
    k = Kid(True)
    dangle = False
    if monkey and right in ("down", "hug") and not book and not torch:
        right = "hug"
    else:
        dangle = monkey and left in ("down",)
        monkey = monkey and right == "hug"
    if shadow: cast_shadow(x, y, 12*s, 2.2*s)
    SWEATER = P.SWEATER; OVER = P.DUNGAREES
    with T(x, y, s, flip):
        hanka_hair_back(k)
        draw_legs(k, legs, OVER, stripes=False, boots=P.HANKA_BOOTS, boot_top=k.ankle+5.5)
        # dots on boots
        draw_arm(k, -1, left, SWEATER)
        # striped sweater torso
        tors = bez((-3.5, k.sh_y+2.2), (-6.5, k.sh_y+2), (-k.sh_w-1, k.sh_y+0.5), (-k.sh_w-1.3, k.sh_y-3)) + \
               bez((-k.sh_w-1.3, k.sh_y-3), (-10.5, 48), (-10.8, 40), (-10.5, 34)) + [(10.5, 34)] + \
               bez((10.5, 34), (10.8, 40), (10.5, 48), (k.sh_w+1.3, k.sh_y-3)) + \
               bez((k.sh_w+1.3, k.sh_y-3), (k.sh_w+1, k.sh_y+0.5), (6.5, k.sh_y+2), (3.5, k.sh_y+2.2)) + [(0, k.sh_y+0.8)]
        fill(tors, SWEATER)
        C.saveState(); C.clipPath(poly(tors), stroke=0, fill=0)
        for j in range(8): fill([(-20, 36+j*3.2), (20, 36+j*3.2), (20, 37.5+j*3.2), (-20, 37.5+j*3.2)], P.SWEATER_STRIPE)
        C.restoreState()
        offset_shadow(tors, -2, 1, 0.1)
        stroke(tors, LINE, closed=True)
        # dungarees: bib + trousers top
        dung = [(-6, 50), (6, 50), (6.5, 42)] + bez((6.5, 42), (9, 40), (10.8, 36), (11, 29.5)) + [(-11, 29.5)] + \
               bez((-11, 29.5), (-10.8, 36), (-9, 40), (-6.5, 42))
        form(dung, OVER, sdx=-1.8, sdy=1, sh=0.12)
        for sx in (-1, 1):
            stroke(bez((sx*5, 50), (sx*6, 53), (sx*7, 56), (sx*7.3, k.sh_y+1)), LINE*2.4, g=0.0)
            stroke(bez((sx*5, 50), (sx*6, 53), (sx*7, 56), (sx*7.3, k.sh_y+1)), LINE*1.2, g=OVER)
            shape(ell(sx*4.8, 49, 1.0, 1.0, 12), P.DUNGAREE_BUTTON, LINE*0.7)
        pk = rrect(-3.2, 42.5, 6.4, 5, 1)
        stroke(pk, LINE*0.7, closed=True)
        # little heart on pocket
        hx_, hy_ = 0, 45.2
        ht = bez((hx_, hy_-1.3), (hx_-2.2, hy_), (hx_-1.2, hy_+1.5), (hx_, hy_+0.5)) + bez((hx_, hy_+0.5), (hx_+1.2, hy_+1.5), (hx_+2.2, hy_), (hx_, hy_-1.3))
        shape(ht, P.HEART, LINE*0.5)
        stroke(bez((-0.5, 34), (-0.3, 31.5), (0, 30.5), (0, 29.6)), LINE*0.6)
        if monkey:
            import chars3
            chars3.monkey_hug(k)
        h, fa = draw_arm(k, 1, right, SWEATER)
        if torch:
            import chars3
            chars3.torch(h[0], h[1], fa); hand(h[0], h[1], fa)
        if book:
            notebook(0, 44, 0.8, drawing=True); hand(h[0], h[1], fa); hand(-4.5, 42.5, -30)
        if bunny_toy:
            bunny(h[0]+1.5, h[1]-5, 1.0); hand(h[0], h[1], fa)
        if item: item(*h)
        if dangle:
            import chars3
            _, _, lh, lfa = arm_pts(k, -1, left)
            chars3.monkey_dangle(lh[0], lh[1])
        # neck + head
        shape([(-2.4, k.sh_y+4), (2.4, k.sh_y+4), (2.5, k.sh_y+0.8), (-2.5, k.sh_y+0.8)], P.SKIN, 0)
        stroke([(-2.3, k.sh_y+4.2), (-2.5, k.sh_y+1)], LINE*0.8); stroke([(2.3, k.sh_y+4.2), (2.5, k.sh_y+1)], LINE*0.8)
        # collar of sweater
        shape(bez((-4, k.sh_y+2.1), (-2, k.sh_y+0.2), (2, k.sh_y+0.2), (4, k.sh_y+2.1)) + bez((4, k.sh_y+2.1), (2, k.sh_y+1.1), (-2, k.sh_y+1.1), (-4, k.sh_y+2.1)), SWEATER, LINE*0.8)
        ho = head_outline(k)
        shape(ho, P.SKIN)
        face(0, k.hy, k.hr, mood, look, young=True)
        hanka_hair_front(k)

# ------------------------------------------------------------------ JOEY (clean)
BLK = P.JOEY_BLACK
def notch(pts, amp=0.9, every=5):
    P = resample(pts, 1.0); out = []
    for i in range(len(P)):
        a = P[max(0, i-1)]; b = P[min(len(P)-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        kk = amp if i % every == every-1 else 0
        out.append((P[i][0]-dy/L*kk, P[i][1]+dx/L*kk))
    return out

def joey(x, y, s=1.0, flip=False, mood="happy", pose="stand", shadow=True):
    sniff = pose == "sniff"
    if shadow: cast_shadow(x + (2*s if not flip else -2*s), y, 26*s, 2.8*s)
    with T(x, y, s, flip):
        # tail
        tail = notch(bez((-19, 32), (-28, 30), (-30, 18), (-27, 8)), 1.0, 4) + bez((-27, 8), (-25.5, 4.5), (-22, 5.5), (-22.5, 9)) + \
               notch(bez((-22.5, 9), (-23.5, 16), (-22, 24), (-17, 26)), 1.1, 4)
        form(tail, BLK, sh=0)
        shape(notch(bez((-27.8, 11), (-29, 5), (-24, 3), (-22.3, 8)), 0.6, 3) + [(-24.5, 11)], 1.0)
        # far legs
        fb = [(-12, 24), (-10.5, 14), (-13.5, 7), (-11.5, 2)]
        ff = [(13, 23), (13.5 + (2.5 if sniff else 0), 12), (14 + (4.5 if sniff else 0), 2)]
        for lg in (fb, ff):
            tube(lg, 5.5, 3.8, P.JOEY_FAR_LEG, sh=0)
            px, py = lg[-1]; shape(ell(px+1.4, py-0.4, 2.9, 1.7, 14), P.JOEY_FAR_LEG)
        # body
        body = bez((-20.5, 29), (-19, 38.5), (0, 39.5), (14, 38)) + bez((14, 38), (20, 37), (23, 31), (21, 23)) + \
               notch(bez((21, 23), (12, 20), (0, 23.5), (-13, 21.5)), 0.9, 4) + bez((-13, 21.5), (-20, 21), (-22.5, 25), (-20.5, 29))
        form(body, BLK, sh=0)
        stroke(bez((-8, 37.8), (-2, 38.7), (5, 38.6), (11, 37.5)), LINE*1.4, g=0.45)
        stroke(bez((-18.5, 23.5), (-19.5, 30), (-15, 33.5), (-9.5, 31.5)), LINE*0.7, g=0.5)
        # near legs
        nb = [(-15.5, 26), (-13, 15), (-17.5, 8), (-15.5, 2.2)]
        o = tube(nb, 7.0, 4.2, BLK, sh=0)
        C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
        fill([(-26, -1), (-6, -1), (-6, 9.5), (-26, 9.5)], 1.0); C.restoreState(); stroke(o, LINE, closed=True)
        nf = [(9.5, 24), (10.5 + (2.5 if sniff else 0), 12), (11 + (4.5 if sniff else 0), 2.2)]
        tube(nf, 6.5, 4.3, 1.0, sh=0.08)
        for lg in (nb, nf):
            px, py = lg[-1]
            shape(ell(px+1.6, py-0.6, 3.3, 1.9, 16), 1.0)
            for kx in (0.2, 1.5, 2.8): stroke([(px+kx, py-2.3), (px+kx-0.2, py-1.3)], LINE*0.5)
        HX, HY = (30, 22) if sniff else (25, 43)
        # neck + ruff
        form(notch(bez((11, 37), (15, 42), (HX-8, HY+6), (HX-6, HY+4)), 0.7, 5) + [(HX+2, HY-4), (22, 24)], BLK, sh=0)
        ruff = notch(bez((13, 36), (15, 40), (HX-7, HY+1), (HX-4, HY-2)), 0.8, 4) + \
               notch(bez((HX-4, HY-2), (HX+3, HY-9), (27, 22), (21, 17.5)), 1.1, 3) + \
               notch(bez((21, 17.5), (18, 23), (14, 29), (13, 36)), 0.8, 4)
        form(ruff, 1.0, sdx=1.5, sdy=1.2, sh=0.1)
        for (a, b_) in (((17, 30), (18.5, 27.5)), ((20, 25), (21, 22.5)), ((16, 34), (17.5, 31.5))):
            stroke([a, b_], LINE*0.5, g=0.45)
        col = ell(HX-4.3, HY-4, 5.4, 1.4, 20, rot=-50 if not sniff else 25)
        shape(col, P.JOEY_COLLAR, LINE*0.8)
        shape(ell(HX-2.2, HY-7.6 if not sniff else HY-2, 1.0, 1.0, 12), P.JOEY_TAG, LINE*0.6)
        # head (local frame)
        C.saveState(); C.translate(HX, HY); C.scale(1.1, 1.18); _SC.append(_SC[-1]*1.14)
        ear2 = bez((-4, 4), (-6.5, 8), (-5.5, 11.5), (-3.8, 11)) + [(-1, 6)]
        shape(ear2, 0.1)
        sk = bez((-6, 0), (-6.5, 6), (-1, 8), (3.5, 6.5)) + bez((3.5, 6.5), (6, 5), (7, 3), (8, 2)) + \
             bez((8, 2), (11, 1.6), (12.5, 0.6), (12.8, -1)) + bez((12.8, -1), (12.8, -3), (9, -4.2), (6, -4.5)) + \
             bez((6, -4.5), (2, -5.5), (-3, -5.5), (-6, 0))
        fill(sk, BLK)
        blaze = bez((1.2, 7.6), (2.2, 5), (4.5, 3.2), (7.8, 2.1)) + bez((7.8, 2.1), (11, 1.6), (12.5, 0.6), (12.8, -1)) + \
                bez((12.8, -1), (12.8, -3), (9, -4.2), (6, -4.5)) + bez((6, -4.5), (3.5, -4), (2.5, -1), (3, 1)) + \
                bez((3, 1), (2, 3), (0.8, 5), (0.3, 7.6))
        fill(blaze, 1.0)
        stroke(sk, LINE, closed=True)
        ns = bez((11.6, 0.4), (12.9, 1.3), (14, 0.6), (13.8, -0.8)) + bez((13.8, -0.8), (13.3, -1.8), (11.9, -1.4), (11.6, 0.4))
        shape(ns, 0.05, LINE*0.7)
        dot(12.9, 0.6, 0.3, 0.9)
        if mood in ("happy", "bark"):
            m = bez((5.5, -2.6), (7.8, -6), (11, -5.6), (12.6, -2.6)) + bez((12.6, -2.6), (10, -3.4), (7.6, -3.4), (5.5, -2.6))
            shape(m, P.JOEY_MOUTH, LINE*0.7)
            if mood == "happy":
                tg = bez((7.8, -4.0), (7.6, -8.2), (10.6, -8.4), (10.6, -4.4)) + [(7.8, -4.0)]
                shape(tg, P.JOEY_TONGUE, LINE*0.7)
                stroke([(9.2, -4.8), (9.1, -7.2)], LINE*0.4)
        else:
            stroke(bez((6, -3.2), (8.5, -4), (11, -3.8), (12.5, -2.6)), LINE*0.7)
        ex_, ey_ = 4.2, 2.6
        if mood == "sleepy":
            stroke(bez((ex_-1.3, ey_), (ex_-0.4, ey_-0.8), (ex_+0.6, ey_-0.8), (ex_+1.4, ey_)), LINE*0.9, g=0.9)
        else:
            shape(ell(ex_, ey_, 1.35, 1.45, 16), 0.95, LINE*0.5)
            dot(ex_+0.25, ey_, 0.85, 0.0); dot(ex_+0.6, ey_+0.45, 0.33, 1.0)
        stroke(bez((ex_-1.1, ey_+2.1), (ex_-0.3, ey_+2.7), (ex_+0.6, ey_+2.7), (ex_+1.3, ey_+2.2)), LINE*0.6, g=0.6)
        e1 = bez((-1.5, 6.6), (-2.5, 10), (-1, 14), (1.5, 14.5)) + bez((1.5, 14.5), (3.5, 14.6), (4.5, 12.8), (4, 11.2)) + [(3, 6.2)]
        shape(e1, BLK)
        shape([(0.8, 14.3), (4.2, 12.5), (4.6, 10.4), (2.4, 12)], 0.4, LINE*0.7)
        _SC.pop(); C.restoreState()
