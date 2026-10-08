from __future__ import annotations
import math, json, argparse, os, copy
from dataclasses import dataclass, asdict, field
from build123d import Box, Cylinder, Pos, Rot, Axis, Plane, Spline, ThreePointArc, Line, Wire, Face, revolve, fillet, Compound, Part, export_step, export_stl, export_gltf, Unit, Location
import numpy as np
from build123d import Vertex, Polyline, make_face, Edge, Vector, Sketch, chamfer, fillet, revolve, loft, Box, Cylinder, Sphere, Pos, Rot, Location, Axis, Plane, GeomType, Face, Wire, Spline, Line, ThreePointArc, Compound, Part, extrude, export_step, export_gltf, Unit
SYS = dict(M4_TAP=3.3, M4_MAJOR=4.0, M4_CLEAR=4.3, M5_CLEAR=5.5, WALL_MIN=1.5, ROOF_MIN=1.0, ENG_MIN=4.0, BAR_WALL_MIN=1.0, SPIGOT_D=5.0, SPIGOT_H=1.0, CBORE_D=5.1, CBORE_H=1.2, POST_TAP_DEPTH=9.0, CONTACT_MIN=10.0, PRELOAD_N=1200.0, ROD_ROOF=1.2, PIN_D=1.0, PIN_OFF=2.3, PIN_DEPTH=3.0, PIN_BAR_DEPTH=2.5, CLEAR_MIN=30.0, KNOB_CLEAR_MIN=15.0, E=95000.0, F_TEST=100.0, DEFL_MAX=0.5, STRESS_MAX=150.0, LEVER_F=200.0, LEVER_STRESS_MAX=200.0, RHO={'brass': 0.00828, 'pol': 0.00828, 'matte': 0.00828, 'oak': 0.0007, 'ash': 0.00068, 'leather': 0.00095, 'steel': 0.00785}, SPACINGS=(96, 128, 160, 224, 320), COLLAR_W=6.0, DOOR_SPINDLE=8.0, WIN_SPINDLE=7.0, WIN_SCREW_SPACING=43.0, PZ_DIST=72.0, BB_DIST=72.0, WC_DIST=78.0, ROSE_BORE=15.2, LEVER_SPIGOT_D=15.0, LEVER_SPIGOT_H=4.0)
DIRS = ('OT', 'PN', 'OB', 'OS', 'KS')
DIR_NAMES = {'OT': 'OTOCZAK', 'PN': 'PION', 'OB': 'OBRĄCZKA', 'OS': 'OSIKA', 'KS': 'KASKADA'}

@dataclass
class Mod:
    code: str
    kind: str
    dir: str
    parts: dict
    meta: dict = field(default_factory=dict)

    def mass_g(self):
        return sum((p.volume * SYS['RHO'][m] for p, m in self.parts.values()))

    def placed(self, loc):
        return {k: (loc * p, m) for k, (p, m) in self.parts.items()}

    def solid(self):
        ps = [p for p, _ in self.parts.values()]
        out = ps[0]
        for p in ps[1:]:
            out = out + p
        return out

def _cyl(d, h, x=0.0, y=0.0, z0=0.0):
    return Pos(x, y, z0 + h / 2) * Cylinder(d / 2, h)

def _profile_face(pts, plane='XZ', fillets=None):
    P = [(u, 0, v) for u, v in pts] if plane == 'XZ' else [(u, v, 0) for u, v in pts]
    f = make_face(Polyline(*P, close=True))
    if fillets:
        for i, rad in sorted(fillets.items()):
            p = Vector(*P[i])
            vs = [v for v in f.vertices() if (v.center() - p).length < 1e-05]
            if vs:
                f = fillet(vs, rad)
                f = f.faces()[0] if hasattr(f, 'faces') else f
    return f

def rev_z(pts, fillets=None):
    return revolve(_profile_face(pts, 'XZ', fillets), Axis.Z, 360)

def _spline_face_x(L, r, dome):
    a = dome
    n = 10
    right = [(L / 2 - a + a * math.sin(t), r * math.cos(t)) for t in np.linspace(0, math.pi / 2, n)]
    left = [(-x, y) for x, y in reversed(right)]
    e1 = Spline(*[(x, y, 0) for x, y in left], tangents=[(0, 1, 0), (1, 0, 0)])
    e2 = Line((left[-1][0], r, 0), (right[0][0], r, 0))
    e3 = Spline(*[(x, y, 0) for x, y in right], tangents=[(1, 0, 0), (0, -1, 0)])
    e4 = Line((L / 2, 0, 0), (-L / 2, 0, 0))
    return Face(Wire([e1, e2, e3, e4]))

def rod_x(L, d, dome_frac=0.55):
    return revolve(_spline_face_x(L, d / 2, d / 2 * dome_frac), Axis.X, 360)

def ecc(cc):
    return max(14.0, 0.14 * cc)

def bar_L(cc):
    return round(cc + 2 * ecc(cc), 2)

def _pin_xy(x0, sgn=1):
    o = SYS['PIN_OFF']
    return (x0 + o * sgn, o)
ROD_D = {96: 8.0, 128: 8.0, 160: 8.0, 224: 8.0, 320: 10.0}
OS_SLEEVE_D = {96: 12.0, 128: 12.0, 160: 12.0, 224: 13.0, 320: 15.0}

def rod_tap_depth(d):
    r, a = (d / 2, SYS['M4_TAP'] / 2)
    return round(r + math.sqrt(r * r - a * a) - SYS['ROOF_MIN'] - 0.05, 2)

def bar_PN(cc):
    w, h = (7.0, 12.0) if cc < 320 else (8.0, 14.0)
    L = bar_L(cc)
    b = Pos(0, 0, h / 2) * Box(L, w, h)
    b = chamfer(b.edges(), 0.35)
    td = 7.5
    for x in (-cc / 2, cc / 2):
        b -= _cyl(SYS['M4_TAP'], td, x, 0, -0.01)
        px, py = _pin_xy(x, 1 if x < 0 else -1)
        b -= _cyl(SYS['PIN_D'] + 0.02, SYS['PIN_BAR_DEPTH'], px, py, -0.01)
    code = f'PN-F{cc}'
    return Mod(code, 'bar', 'PN', {f'brass_{code}': (b, 'brass')}, dict(seat='F', cc=cc, L=L, w=w, h=h, tap_depth=td, pins=True, sect=f'FIN {w:g}×{h:g}', load=[f'brass_{code}']))

def bar_KS(cc, big=None):
    big = cc >= 320 if big is None else big
    w1, h1, w2, h2, ins = (13.0, 4.2, 8.0, 4.2, 3.5) if big else (11.0, 3.5, 6.6, 3.5, 3.0)
    L = bar_L(cc)
    t1 = Pos(0, 0, h1 / 2) * Box(L, w1, h1)
    t1 = chamfer(t1.edges(), 0.25)
    t2 = Pos(0, 0, h1 + h2 / 2 - 0.005) * Box(L - 2 * ins, w2, h2 + 0.01)
    t2 = chamfer(t2.edges().filter_by_position(Axis.Z, h1 + 0.1, 99), 0.25)
    b = t1 + t2
    td = h1 + h2 - 1.5
    for x in (-cc / 2, cc / 2):
        b -= _cyl(SYS['M4_TAP'], td, x, 0, -0.01)
        px, py = _pin_xy(x, 1 if x < 0 else -1)
        b -= _cyl(SYS['PIN_D'] + 0.02, SYS['PIN_BAR_DEPTH'], px, py, -0.01)
    code = f'KS-S{cc}' + ('L' if big else '') + ('-STD' if cc >= 320 and (not big) else '')
    return Mod(code, 'bar', 'KS', {f'brass_{code}': (b, 'brass')}, dict(seat='F', cc=cc, L=L, w=w1, h=h1 + h2, tap_depth=td, pins=True, sect=f'2-stopniowy {w1:g}×{h1:g} + {w2:g}×{h2:g}', load=[f'brass_{code}']))

def bar_OB(cc, d=None):
    d = d or ROD_D[cc]
    L = bar_L(cc)
    b = rod_x(L, d)
    td = rod_tap_depth(d)
    for x in (-cc / 2, cc / 2):
        b -= _cyl(SYS['M4_TAP'], td, x, 0, -d / 2 - 0.01)
    code = f'OB-R{cc}' + ('' if d == ROD_D[cc] else f'-D{d:g}')
    return Mod(code, 'bar', 'OB', {f'matte_{code}': (b, 'matte')}, dict(seat='C', cc=cc, L=L, rod_d=d, vis_d=d, tap_depth=td, pins=False, sect=f'pręt Ø{d:g}', load=[f'matte_{code}']))

def bar_OS(cc, species='DB'):
    d, D = (ROD_D[cc], OS_SLEEVE_D[cc])
    L = bar_L(cc)
    cap_t, cap_in = (2.6, 1.5)
    core = rod_x(L - 2 * (cap_t - cap_in), d, dome_frac=0.0001) if False else None
    cl = L - 2 * (cap_t - cap_in)
    core = Rot(0, 90, 0) * Cylinder(d / 2, cl)
    core = chamfer(core.edges(), 0.3)
    td = rod_tap_depth(d)
    for x in (-cc / 2, cc / 2):
        core -= _cyl(SYS['M4_TAP'], td, x, 0, -d / 2 - 0.01)
    R = D / 2
    cp = [(0, 0), (R - 0.3, 0), (R, 0.3), (R, cap_t * 0.35)]
    cp += [(R * math.cos(a), cap_t * 0.35 + cap_t * 0.65 * math.sin(a)) for a in np.linspace(0.15, math.pi / 2, 8)]
    cap = rev_z(cp)
    cap -= _cyl(d + 0.02, cap_in, 0, 0, -0.01)
    capR = Pos(L / 2 - cap_t, 0, 0) * Rot(0, 90, 0) * cap
    capL = Pos(-L / 2 + cap_t, 0, 0) * Rot(0, -90, 0) * cap
    g = SYS['COLLAR_W'] / 2 + 0.1
    segs = [(-L / 2 + cap_t + 0.05, -cc / 2 - g), (-cc / 2 + g, cc / 2 - g), (cc / 2 + g, L / 2 - cap_t - 0.05)]
    mat = 'oak' if species == 'DB' else 'ash'
    parts = {}
    code = f'OS-{species}{cc}'
    parts[f'brass_{code}_core'] = (core, 'brass')
    parts[f'brass_{code}_capL'] = (capL, 'brass')
    parts[f'brass_{code}_capR'] = (capR, 'brass')
    for i, (a, b_) in enumerate(segs):
        ln = b_ - a
        s = Rot(0, 90, 0) * (Cylinder(R, ln) - Cylinder(d / 2 + 0.05, ln + 1))
        s = fillet(s.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > R - 0.01), 0.6)
        parts[f'{mat}_{code}_s{i}'] = (Pos((a + b_) / 2, 0, 0) * s, mat)
    return Mod(code, 'bar', 'OS', parts, dict(seat='C', cc=cc, L=L, rod_d=d, vis_d=D, tap_depth=td, pins=False, species=species, sect=f"rdzeń Ø{d:g} + {('dąb' if species == 'DB' else 'jesion')} Ø{D:g}", load=[f'brass_{code}_core']))

def collar_dims(rod_d, vis_d):
    rr, vr = (rod_d / 2, vis_d / 2)
    f = vr if vr >= rr + 1.0 else rr + 1.0
    Ro = max(math.sqrt(f * f + 2.8 ** 2), vr + 0.3)
    Ro = math.ceil(Ro * 20) / 20
    return (f, Ro)

def make_collar(rod_d, vis_d, style='R'):
    f, Ro = collar_dims(rod_d, vis_d)
    W = SYS['COLLAR_W']
    c = Rot(0, 90, 0) * Cylinder(Ro, W)
    if style == 'R':
        c = fillet(c.edges(), 1.2)
    else:
        c = chamfer(c.edges(), 0.3)
    c = Pos(0, 0, f) * c
    c -= Pos(0, 0, -50) * Box(W + 2, 3 * Ro, 100)
    c -= Pos(0, 0, f) * Rot(0, 90, 0) * Cylinder(rod_d / 2 + 0.03, W + 2)
    c -= _cyl(SYS['M4_CLEAR'], f, 0, 0, -0.01)
    code = f'C{style}{rod_d:g}-{vis_d:g}'
    mat = 'pol' if style == 'R' else 'brass'
    land_w = 2 * math.sqrt(max(Ro * Ro - f * f, 0))
    return Mod(code, 'collar', 'SYS', {f'{mat}_{code}': (c, mat)}, dict(rod_d=rod_d, vis_d=vis_d, f=f, Ro=Ro, D=2 * Ro, land_w=land_w, style=style))
POST_FAM = {'SR7': dict(shape='round', d=7.0, top_ch=0.4), 'SR8': dict(shape='round', d=8.0, top_ch=0.5), 'SQ7': dict(shape='square', a=7.0, top_ch=0.25), 'SK8': dict(shape='stepped', d=8.0, top_ch=0.4), 'OTD': dict(shape='drop', d=7.2, top_ch=0.0)}

def make_post(fam, H, kind='post', pin_foot=False):
    sp = POST_FAM[fam]
    if sp['shape'] == 'round':
        r = sp['d'] / 2
        p = rev_z([(0, 0), (r, 0), (r, H), (0, H)])
        p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], sp['top_ch'])
        p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.3)
        top = ('circle', sp['d'] - 2 * sp['top_ch'])
    elif sp['shape'] == 'square':
        a = sp['a']
        p = Pos(0, 0, H / 2) * Box(a, a, H)
        p = chamfer(p.edges(), sp['top_ch'])
        top = ('square', a - 2 * sp['top_ch'])
    elif sp['shape'] == 'stepped':
        pts = [(0, 0), (6.5, 0), (6.5, 3.2), (5.25, 3.2), (5.25, 6.4), (4.0, 6.4), (4.0, H), (0, H)]
        p = rev_z(pts)
        p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], sp['top_ch'])
        for zz in (3.2, 6.4):
            es = [e for e in p.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - zz) < 0.0001]
            p = chamfer(es, 0.25)
        p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.3)
        top = ('circle', 8.0 - 0.8)
    else:
        zs = np.linspace(0, H, 9)
        rr = [3.6 + 0.6 * (1 - z / H) ** 2.2 for z in zs]
        pts = [(0, 0)] + [(r_ - (0.25 if i == 0 else 0), z) for i, (r_, z) in enumerate(zip(rr, zs))] + [(0, H)]
        e_sp = Spline(*[(r_, 0, z) for r_, z in zip(rr, zs)])
        w = Wire([Line((0, 0, 0), (rr[0], 0, 0)), e_sp, Line((rr[-1], 0, H), (0, 0, H)), Line((0, 0, H), (0, 0, 0))])
        p = revolve(Face(w), Axis.Z, 360)
        p = fillet(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.3)
        top = ('circle', 7.2)
    p -= _cyl(SYS['CBORE_D'], SYS['CBORE_H'], 0, 0, -0.01)
    tdep = SYS['POST_TAP_DEPTH']
    if H >= 2 * tdep + 2:
        p -= _cyl(SYS['M4_TAP'], tdep + 0.01, 0, 0, H - tdep)
        p -= _cyl(SYS['M4_TAP'], tdep, 0, 0, SYS['CBORE_H'] - 0.01)
        taps = [(H - tdep, H), (SYS['CBORE_H'], SYS['CBORE_H'] + tdep)]
    else:
        p -= _cyl(SYS['M4_TAP'], H + 1, 0, 0, -0.5)
        taps = [(SYS['CBORE_H'], H)]
    pins = []
    if sp['shape'] == 'square':
        o = SYS['PIN_OFF']
        p -= _cyl(SYS['PIN_D'] - 0.02, SYS['PIN_DEPTH'] + 0.01, o, o, H - SYS['PIN_DEPTH'])
        pins.append(('top', o, o))
        if pin_foot:
            p -= _cyl(SYS['PIN_D'] - 0.02, SYS['PIN_DEPTH'], o, o, -0.01)
            pins.append(('foot', o, o))
    pre = 'K' if kind == 'stem' else ''
    code = f'{fam}-{pre}{H:g}'
    return Mod(code, kind, 'SYS', {f'brass_{code}': (p, 'brass')}, dict(fam=fam, H=H, shape=sp['shape'], top=top, taps=taps, pins=pins))

def make_washer(code):
    if code == 'W0':
        return None
    t = 1.0
    if code == 'WR12':
        p = rev_z([(0, 0), (6, 0), (6, t), (0, t)])
        p = fillet(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.45)
        mat = 'pol'
        land = ('circle', 12 - 0.9)
    elif code == 'WR13':
        p = rev_z([(0, 0), (6.5, 0), (6.5, t), (0, t)])
        p = chamfer(p.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.3)
        mat = 'brass'
        land = ('circle', 13 - 0.6)
    elif code == 'WD14':
        t = 1.25
        zs = np.linspace(0, math.pi / 2, 8)
        prof = [(0, 0), (7.0, 0)] + [(4.2 + 2.8 * math.cos(a), 0.35 + 0.9 * math.sin(a)) for a in zs[:-1]] + [(4.2, t), (0, t)]
        p = rev_z(prof)
        mat = 'brass'
        land = ('circle', 8.4)
    elif code == 'WS11':
        p = Pos(0, 0, t / 2) * Box(11, 11, t)
        p = chamfer(p.edges().group_by(Axis.Z)[-1], 0.25)
        mat = 'brass'
        land = ('square', 10.5)
    elif code == 'WT17':
        t = 3.6
        p = rev_z([(0, 0), (8.5, 0), (8.5, 1.2), (6.9, 1.2), (6.9, 2.4), (5.4, 2.4), (5.4, 3.6), (0, 3.6)])
        for zz in (1.2, 2.4, 3.6):
            es = [e for e in p.edges().filter_by(GeomType.CIRCLE) if abs(e.center().Z - zz) < 0.0001 and e.radius > 3]
            p = chamfer(es, 0.2)
        mat = 'brass'
        land = ('circle', 10.4)
    else:
        raise ValueError(code)
    p += _cyl(SYS['SPIGOT_D'], SYS['SPIGOT_H'], 0, 0, t - 0.01)
    p -= _cyl(SYS['M4_CLEAR'], t + SYS['SPIGOT_H'] + 1, 0, 0, -0.5)
    return Mod(code, 'washer', 'SYS', {f'{mat}_{code}': (p, mat)}, dict(t=t, land=land))

def _se_section(x, a, tt, tb, n=2.4, N=40, zc=0.0, axis='X'):
    pts = []
    for k in range(N):
        th = 2 * math.pi * k / N
        c, s = (math.cos(th), math.sin(th))
        y = a * math.copysign(abs(c) ** (2 / n), c)
        z = (tt if s >= 0 else tb) * math.copysign(abs(s) ** (2 / n), s)
        pts.append((x, y, z + zc))
    return pts

def pebble(L, W, tt, tb, zc, nsec=23, x0=0.0, n=2.4, caps=False, endk=0.06):
    secs = []
    ss = np.linspace(-1, 1, nsec)
    for i, s in enumerate(ss):
        if i in (0, nsec - 1) and (not caps):
            continue
        u = math.sin(s * math.pi / 2)
        if i in (0, nsec - 1):
            u, fw, ft = (math.copysign(0.9995, u), endk, endk)
        else:
            fw = (1 - 0.24 * u * u) * (1 - abs(u) ** 6) ** (1 / 6)
            ft = (1 - 0.18 * u * u) * (1 - abs(u) ** 5) ** (1 / 5)
            if caps:
                fw, ft = (max(fw, endk), max(ft, endk))
        pts = _se_section(x0 + u * L / 2, W / 2 * fw, tt * ft, tb * ft, n=n, zc=zc)
        secs.append(Face(Wire([Spline(*pts, periodic=True)])))
    if caps:
        return loft(secs, ruled=False)
    return loft([Vertex(x0 - L / 2, 0, zc)] + secs + [Vertex(x0 + L / 2, 0, zc)], ruled=False)

def _stub(x, y, zs, rs):
    return loft([Pos(x, y, z) * Face(Wire([Edge.make_circle(r)])) for z, r in zip(zs, rs)])

def _blend(body, extra, region, r):
    b = body
    for e in extra:
        b = b + e
    x0, x1, z0, z1 = region
    cand = [e for e in b.edges() if x0 < abs(e.center().X) < x1 and z0 < e.center().Z < z1 and (e.length > 8)]
    try:
        b2 = fillet(cand, r)
        if b2.is_valid:
            return b2
    except Exception:
        pass
    return b

def bar_OT(cc):
    big = cc >= 224
    W, tt, tb = (16.0, 5.4, 4.0) if big else (14.6, 4.9, 3.6)
    L = bar_L(cc) + 6
    S = 19.0
    zc = S + tb
    g = pebble(L, W, tt, tb, zc)
    stubs = [_stub(x, 0, [0, 6, 11, 15, zc - 0.5], [3.6, 3.7, 4.4, 5.6, 5.8]) for x in (-cc / 2, cc / 2)]
    b = _blend(g, stubs, (cc / 2 - 8, cc / 2 + 8, zc - tb - 1.5, zc - 0.2), 2.0)
    td = 8.0
    for x in (-cc / 2, cc / 2):
        b -= _cyl(SYS['M4_TAP'], td, x, 0, -0.01)
    code = f'OT-G{cc}'
    return Mod(code, 'bar', 'OT', {f'brass_{code}': (b, 'brass')}, dict(seat='W', cc=cc, L=L, w=W, h=tt + tb, tap_depth=td, pins=False, land_d=7.2, sect=f'otoczak {W:g}×{tt + tb:g}', load=[f'brass_{code}']))
BAR_GEN = {'OT': bar_OT, 'PN': bar_PN, 'OB': bar_OB, 'OS': bar_OS, 'KS': bar_KS}
KNOB_SIZES = {'OT': {'S': (30, 19, 11.5), 'M': (34, 22, 13), 'L': (38, 25, 14.5)}, 'PN': {'S': 26, 'M': 32, 'L': 40}, 'OB': {'S': 24, 'M': 28, 'L': 34}, 'OS': {'S': 25, 'M': 30, 'L': 35}, 'KS': {'S': 25, 'M': 30, 'L': 35}}

def head(dir_, size):
    k = KNOB_SIZES[dir_][size]
    parts, meta = ({}, dict(round=True, pin=False))
    if dir_ == 'OT':
        Lx, Wy, h = k
        ct, cb = (0.62 * h, 0.38 * h)
        s0 = 6.0
        zc = s0 + cb
        top = (Sphere(1) & Pos(0, 0, 1) * Box(3, 3, 2)).scale(1)
        from build123d import scale as _scale
        top = _scale(top, (Lx / 2, Wy / 2, ct))
        bot = _scale(Sphere(1) & Pos(0, 0, -1) * Box(3, 3, 2), (Lx / 2, Wy / 2, cb))
        hd = Pos(0, 0, zc) * (top + bot)
        st = _stub(0, 0, [0, 2.5, 5, zc - 0.3], [3.6, 3.75, 4.6, 6.0])
        b = _blend(hd, [st], (-1, 9, s0 - 1.5, zc), 1.5)
        b -= _cyl(SYS['M4_TAP'], 8, 0, 0, -0.01)
        parts['brass_head'] = (b, 'brass')
        meta.update(round=False, D=Lx, H=zc + ct, land=('circle', 7.2), tap=8)
    elif dir_ == 'PN':
        a = k
        b = Pos(0, 0, 6) * Box(a, 7, 12)
        b = chamfer(b.edges(), 0.35)
        b -= _cyl(SYS['M4_TAP'], 7.5, 0, 0, -0.01)
        o = SYS['PIN_OFF']
        b -= _cyl(SYS['PIN_D'] + 0.02, SYS['PIN_BAR_DEPTH'], o, o, -0.01)
        parts['brass_head'] = (b, 'brass')
        meta.update(round=False, pin=True, D=a, H=12, land=('rect', 6.3), tap=7.5)
    elif dir_ == 'OB':
        D = k
        bz = 1.4
        disc = rev_z([(0, 3), (D / 2 - bz, 3), (D / 2 - bz, 8.5), (0, 8.5)])
        disc = fillet(disc.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.6)
        boss = _cyl(10, 3.01, 0, 0, 0)
        boss = chamfer(boss.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.3)
        b = disc + boss
        b -= _cyl(SYS['M4_TAP'], 7.0, 0, 0, -0.01)
        ring = rev_z([(D / 2 - bz, 3), (D / 2, 3), (D / 2, 8.5), (D / 2 - bz, 8.5)])
        ring = fillet(ring.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > D / 2 - 0.01), 0.5)
        parts['matte_head'] = (b, 'matte')
        parts['pol_bezel'] = (ring, 'pol')
        meta.update(D=D, H=8.5, land=('circle', 9.4), tap=7.0)
    elif dir_ == 'OS':
        D = k
        base_h, bush_d, bush_h = (3.0, 9.0, 10.0)
        base = rev_z([(0, 0), (D / 2, 0), (D / 2, base_h), (0, base_h)])
        base = chamfer(base.edges().filter_by(GeomType.CIRCLE), 0.3)
        base += _cyl(bush_d, bush_h, 0, 0, base_h - 0.01)
        base -= _cyl(SYS['M4_TAP'], 9.0, 0, 0, -0.01)
        hdome = 0.42 * D
        prof = [(0, base_h)] + [(D / 2 * math.cos(a), base_h + hdome * math.sin(a) ** 0.9) for a in np.linspace(0, math.pi / 2, 12)[:-1]] + [(0, base_h + hdome)]
        dome = rev_z(prof)
        dome -= _cyl(bush_d + 0.05, bush_h + 0.01, 0, 0, base_h - 0.01)
        parts['brass_head'] = (base, 'brass')
        parts['oak_head'] = (dome, 'oak')
        meta.update(D=D, H=base_h + hdome, land=('circle', D - 0.6), tap=9.0)
    elif dir_ == 'KS':
        D = k
        hs = [(D, 4.0), (0.84 * D, 1.7), (0.68 * D, 1.7)]
        z, b = (0.0, None)
        for d, hh in hs:
            c = _cyl(d, hh + (0.01 if b is not None else 0), 0, 0, z - (0.01 if b is not None else 0))
            c = chamfer(c.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.25)
            b = c if b is None else b + c
            z += hh
        b = chamfer(b.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[0], 0.25)
        b -= _cyl(SYS['M4_TAP'], 5.9, 0, 0, -0.01)
        parts['brass_head'] = (b, 'brass')
        meta.update(D=D, H=z, land=('circle', D - 0.5), tap=5.9)
    code = f'{dir_}-K{size}'
    parts = {f"{lab.split('_')[0]}_{code}_{lab.split('_')[1]}": v for lab, v in parts.items()}
    return Mod(code, 'head', dir_, parts, meta)
STEMS = {'SR7-K21': ('SR7', 21), 'SR8-K16': ('SR8', 16), 'SQ7-K24': ('SQ7', 24), 'SK8-K18.5': ('SK8', 18.5), 'OTD-12': ('OTD', 12), 'SR8-12': ('SR8', 12)}

def make_stem(code):
    fam, H = STEMS[code]
    if '-K' not in code:
        return make_post(fam, H)
    return make_post(fam, H, kind='stem', pin_foot=fam == 'SQ7')
LEVER_GEOM = {'OT': dict(sec='pebble 18×11', neck=18.0), 'PN': dict(sec='FIN 8×16', neck=18.0), 'OB': dict(sec='Ø16 + pierścień PB', neck=18.0), 'OS': dict(sec='rdzeń Ø12 + dąb Ø20', neck=18.0), 'KS': dict(sec='2 stopnie 14+9 × 4+4', neck=24.0)}

def lever(dir_, kind='door'):
    door = kind == 'door'
    Larm = 132.0 if door else 110.0
    zc = 46.0 if door else 36.0
    sq = SYS['DOOR_SPINDLE'] if door else SYS['WIN_SPINDLE']
    parts, extra = ({}, {})
    if dir_ == 'OT':
        Lp = Larm + 14
        arm = pebble(Lp, 18, 6.0, 5.0, zc, x0=Lp / 2 - 14, caps=True)
        neck = _stub(0, 0, [0, 8, 20, zc - 4, zc], [9.0, 7.6, 6.6, 6.4, 6.4])
        b = _blend(arm, [neck], (-1, 12, zc - 9, zc - 2), 3.0)
    elif dir_ == 'PN':
        arm = Pos((Larm - 9) / 2, 0, zc) * Box(Larm + 9, 8, 16)
        neck = Pos(0, 0, (zc + 8) / 2) * Box(18, 18, zc + 8)
        b = arm + neck
        b = chamfer(b.edges(), 0.4)
    elif dir_ == 'OB':
        arm = Pos(Larm / 2 + 4, 0, zc) * Rot(0, 0, 0) * rod_x(Larm - 8 + 8, 16)
        arm = Pos(-0.0, 0, 0) * arm
        neck = _cyl(16, zc, 0, 0, 0) + Pos(0, 0, zc) * Sphere(8)
        foot = rev_z([(0, 0), (9, 0), (9, 3.0), (8, 4.0), (0, 4.0)])
        b = arm + neck + foot
        b -= rev_z([(7.0, 7.0), (8.5, 7.0), (8.5, 10.0), (7.0, 10.0)])
        ring = rev_z([(7.0, 7.0), (9.6, 7.0), (9.6, 10.0), (7.0, 10.0)])
        ring = fillet(ring.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > 9.5), 0.6)
        extra['pol_ring'] = (ring, 'pol')
    elif dir_ == 'OS':
        core = Pos(Larm / 2, 0, zc) * Rot(0, 90, 0) * Cylinder(6, Larm)
        neck = rev_z([(0, 0), (9, 0), (9, 1), (8, 2), (8, zc + 1), (0, zc + 1)])
        neck += Pos(0, 0, zc) * Sphere(8)
        b = core + neck
        x0, x1 = (12.0, Larm - 3.0)
        sl = Pos((x0 + x1) / 2, 0, zc) * Rot(0, 90, 0) * (Cylinder(10, x1 - x0) - Cylinder(6.05, x1 - x0 + 1))
        sl = fillet(sl.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > 9.9), 1.0)
        cap = rev_z([(0, 0), (9.7, 0), (10, 0.3), (10, 1.0)] + [(10 * math.cos(a), 1.0 + 2.2 * math.sin(a)) for a in np.linspace(0.2, math.pi / 2, 7)])
        cap -= _cyl(12.05, 1.5, 0, 0, -0.01)
        b = b + Pos(x1, 0, zc) * Rot(0, 90, 0) * Cylinder(6, 1.5)
        extra['oak_sleeve'] = (sl, 'oak')
        extra['brass_cap'] = (Pos(x1, 0, zc) * Rot(0, 90, 0) * cap, 'brass')
    elif dir_ == 'KS':
        t1 = Pos(Larm / 2, 0, zc - 2) * Box(Larm, 14, 4)
        t1 = chamfer(t1.edges(), 0.25)
        t2 = Pos(Larm / 2 - 1.5, 0, zc + 1.995) * Box(Larm - 3, 9, 4.01)
        t2 = chamfer(t2.edges().filter_by_position(Axis.Z, zc + 0.1, 99), 0.25)
        neck = None
        z = 0.0
        for d, hh in ((24, 3.0), (19, 3.0), (15, zc + 4 - 6.0)):
            c = _cyl(d, hh + (0.01 if neck is not None else 0), 0, 0, z - (0.01 if neck is not None else 0))
            c = chamfer(c.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.25)
            neck = c if neck is None else neck + c
            z += hh
        b = t1 + t2 + neck
    b += _cyl(SYS['LEVER_SPIGOT_D'], SYS['LEVER_SPIGOT_H'] + 0.01, 0, 0, -SYS['LEVER_SPIGOT_H'])
    sb = sq + 0.05
    bore_d = 18.0 if door else 14.0
    b -= Pos(0, 0, -SYS['LEVER_SPIGOT_H'] - 0.01 + bore_d / 2) * Box(sb, sb, bore_d)
    grub_z = 4.6 if dir_ == 'OB' else 8.0
    if door:
        b -= Pos(0, -4.5, grub_z) * Rot(90, 0, 0) * Cylinder(SYS['M4_TAP'] / 2, 9)
    code = f"{dir_}-{('L' if door else 'O')}"
    lab = 'matte' if dir_ == 'OB' else 'brass'
    parts[f'{lab}_{code}'] = (b, lab)
    for k_, v in extra.items():
        parts[f"{k_.split('_')[0]}_{code}_{k_.split('_')[1]}"] = v
    if not door:
        parts = {k_: (Rot(0, 0, -90) * p, m) for k_, (p, m) in parts.items()}
    return Mod(code, 'lever' if door else 'winhandle', dir_, parts, dict(Larm=Larm, zc=zc, spindle=sq, sec=LEVER_GEOM[dir_]['sec'], load=[f'{lab}_{code}'], grub_z=grub_z, proj=None))

def _outline(dir_, kind):
    parts = {}
    if kind == 'door':
        h = 9.0
        if dir_ == 'PN':
            b = Pos(0, 0, -h / 2) * Box(50, 50, h)
            b = chamfer(b.edges().group_by(Axis.Z)[-1], 0.6)
            b = chamfer(b.edges().filter_by(Axis.Z), 0.3)
            pocket = Pos(0, 0, -h + 1.5) * Box(46.6, 46.6, 3.0)
        elif dir_ == 'KS':
            b = None
            z = -h
            for d in (52, 44, 36):
                c = _cyl(d, 3.0 + (0.01 if b is not None else 0), 0, 0, z - (0.01 if b is not None else 0))
                c = chamfer(c.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.25)
                b = c if b is None else b + c
                z += 3.0
            pocket = _cyl(48.6, 3.0, 0, 0, -h - 0.01)
        elif dir_ == 'OT':
            prof = [(0, -h), (26, -h), (26, -h + 2.0)]
            prof += [(17 + 9 * math.cos(a) ** 0.8, -h + 2.0 + 7.0 * math.sin(a) ** 1.25) for a in np.linspace(0.12, math.pi / 2, 10)]
            prof += [(0, 0)]
            b = rev_z(prof)
            pocket = _cyl(48.6, 3.0, 0, 0, -h - 0.01)
        elif dir_ == 'OB':
            b = rev_z([(0, -h), (24.5, -h), (24.5, 0), (0, 0)])
            b = fillet(b.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.6)
            ring = rev_z([(24.5, -h), (26, -h), (26, 0), (24.5, 0)])
            ring = fillet(ring.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > 25.9).group_by(Axis.Z)[-1], 0.6)
            parts['pol_ring'] = (ring, 'pol')
            pocket = _cyl(46.0, 3.0, 0, 0, -h - 0.01)
        else:
            b = rev_z([(0, -h), (26, -h), (26, 0), (0, 0)])
            b = chamfer(b.edges().filter_by(GeomType.CIRCLE), 0.3)
            b -= rev_z([(10.5, -2.0), (21.0, -2.0), (21.0, 0.1), (10.5, 0.1)])
            inl = rev_z([(10.55, -2.0), (20.95, -2.0), (20.95, 0), (10.55, 0)])
            inl = chamfer(inl.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.3)
            parts['oak_inlay'] = (inl, 'oak')
            pocket = _cyl(48.6, 3.0, 0, 0, -h - 0.01)
    else:
        h = 12.0
        W, Hh = (29.0, 72.0)
        if dir_ == 'KS':
            b = None
            z = -h
            for i, (w_, l_) in enumerate(((29, 72), (23, 66), (17, 60))):
                c = Pos(0, 0, z + 2.0 - (0.005 if i else 0)) * Box(w_, l_, 4.0 + (0.01 if i else 0))
                c = chamfer(c.edges().group_by(Axis.Z)[-1], 0.25)
                b = c if b is None else b + c
                z += 4.0
        else:
            r_c = {'PN': 0.6, 'OT': 8.0, 'OB': 6.0, 'OS': 3.0}[dir_]
            b = Pos(0, 0, -h / 2) * Box(W, Hh, h)
            b = fillet(b.edges().filter_by(Axis.Z), r_c) if r_c > 1 else chamfer(b.edges().filter_by(Axis.Z), r_c)
            if dir_ == 'OT':
                b = fillet(b.edges().group_by(Axis.Z)[-1], 5.0)
            elif dir_ == 'OB':
                b = fillet(b.edges().group_by(Axis.Z)[-1], 0.8)
                b -= rev_z([(7.7, -0.8), (10.05, -0.8), (10.05, 0.1), (7.7, 0.1)])
                ring = rev_z([(7.75, -0.8), (10.0, -0.8), (10.0, 0.0), (7.75, 0.0)])
                ring = chamfer(ring.edges().filter_by(GeomType.CIRCLE).filter_by(lambda e: e.radius > 9.9).group_by(Axis.Z)[-1], 0.15)
                parts['pol_ring'] = (ring, 'pol')
            elif dir_ == 'OS':
                b = chamfer(b.edges().group_by(Axis.Z)[-1], 0.3)
            else:
                b = chamfer(b.edges().group_by(Axis.Z)[-1], 0.6)
        pocket = Pos(0, 0, -h + 2.0) * Box(W - 4, Hh - 4, 4.0)
    return (b, pocket, parts, h)

def rose(dir_, kind='door'):
    b, pocket, parts, h = _outline(dir_, kind)
    b -= pocket
    b -= _cyl(SYS['ROSE_BORE'], h + 2, 0, 0, -h - 1)
    code = f"{dir_}-{('R' if kind == 'door' else 'RO')}"
    lab = 'matte' if dir_ == 'OB' else 'brass'
    out = {f'{lab}_{code}': (b, lab)}
    for k_, v in parts.items():
        out[f"{k_.split('_')[0]}_{code}_{k_.split('_')[1]}"] = v
    if kind == 'door':
        base = Pos(0, 0, -h + 1.5) * (Box(46.4, 46.4, 2.99) if dir_ == 'PN' else Cylinder(23.1 if dir_ != 'OB' else 22.8, 2.99))
        base -= _cyl(SYS['ROSE_BORE'], 10, 0, 0, -h - 2)
        for y in (-19.0, 19.0):
            base -= _cyl(4.3, 10, 0, y, -h - 2)
        meta = dict(h=h, D=50 if dir_ == 'PN' else 52, bolts='2× M4 przelotowe (ukryte)')
    else:
        base = Pos(0, 0, -h + 2.0) * Box(24.8, 67.8, 3.99)
        base -= _cyl(SYS['ROSE_BORE'], 10, 0, 0, -h - 2)
        for y in (-SYS['WIN_SCREW_SPACING'] / 2, SYS['WIN_SCREW_SPACING'] / 2):
            base -= _cyl(SYS['M5_CLEAR'], 10, 0, y, -h - 2)
        meta = dict(h=h, W=29, Hh=72, screws='2× M5 @ 43 (DIN 18267)')
    out[f'steel_{code}_base'] = (base, 'steel')
    return Mod(code, 'rose' if kind == 'door' else 'winrose', dir_, out, meta)

def escutcheon(dir_, typ):
    b, pocket, parts, h = _outline(dir_, 'door')
    b -= pocket
    ins = {}
    if typ == 'PZ':
        cut = _cyl(17.4, h + 2, 0, 8.0, -h - 1) + Pos(0, 8.0 - 12.25, -h / 2) * Box(10.4, 24.5, h + 2)
        axis = 8.0
    elif typ == 'BB':
        cut = _cyl(9.0, h + 2, 0, 5.0, -h - 1) + Pos(0, 5.0 - 7.0, -h / 2) * Box(4.6, 14.0, h + 2)
        axis = 5.0
    else:
        cut = _cyl(SYS['ROSE_BORE'], h + 2, 0, 0, -h - 1)
        axis = 0.0
    b -= cut
    parts = {k_: (p_ - cut, m_) for k_, (p_, m_) in parts.items()}
    parts = {k_: v for k_, v in parts.items() if v[0].volume > 0.001}
    if typ not in ('PZ', 'BB'):
        if typ == 'WCi':
            tt = _cyl(SYS['LEVER_SPIGOT_D'], 4.01, 0, 0, -4.0) + _cyl(18, 3.0, 0, 0, 0)
            wing = Pos(0, 0, 3.0 + 7.0) * Box(30, 6.5, 14)
            if dir_ in ('OT', 'OB', 'OS'):
                wing = fillet(wing.edges().filter_by(Axis.Y), 2.8)
            else:
                wing = chamfer(wing.edges(), 0.4)
            tt = tt + wing
            tt -= Pos(0, 0, -4.0 + 5.0) * Box(8.05, 8.05, 10.0)
            ins[('pol' if dir_ == 'OB' else 'brass') + '_turn'] = (tt, 'pol' if dir_ == 'OB' else 'brass')
        else:
            dr = _cyl(SYS['LEVER_SPIGOT_D'], 4.01, 0, 0, -4.0) + _cyl(18, 2.0, 0, 0, 0)
            dr = chamfer(dr.edges().filter_by(GeomType.CIRCLE).group_by(Axis.Z)[-1], 0.3)
            dr -= Pos(0, 0, 2.0) * Box(12, 1.6, 2.4)
            ins['brass_release'] = (dr, 'brass')
    code = f'{dir_}-E{typ}'
    lab = 'matte' if dir_ == 'OB' else 'brass'
    out = {f'{lab}_{code}': (b, lab)}
    for k_, v in list(parts.items()) + list(ins.items()):
        out[f"{k_.split('_')[0]}_{code}_{k_.split('_')[1]}"] = v
    return Mod(code, 'esc', dir_, out, dict(h=h, axis=axis, typ=typ))

@dataclass
class Assy:
    name: str
    items: list = field(default_factory=list)
    meta: dict = field(default_factory=dict)
    mods: dict = field(default_factory=dict)

    def add(self, mod, loc, tag, role=None):
        if mod is None:
            return
        self.mods[mod.code] = mod
        for lab, (p, m) in mod.parts.items():
            self.items.append([f'{lab}__{tag}', loc * p, m, mod.code, role or mod.kind, loc, lab])

    def mass_g(self):
        return sum((it[1].volume * SYS['RHO'][it[2]] for it in self.items))

    def bom(self):
        out = {}
        for it in self.items:
            out[it[3]] = out.get(it[3], 0)
        for code in out:
            out[code] = len({it[0].split('__')[1] for it in self.items if it[3] == code})
        return out

    def role(self, *roles):
        return [it for it in self.items if it[4] in roles]
FINISH_DEFAULT = {'OT': 'SB', 'PN': 'SB', 'OB': 'SB.PB', 'OS': 'SB', 'KS': 'SB'}

def pull_sku(bar, post, washer, collar, finish):
    s = f"{bar.code}/{post.code}/{(washer.code if washer else 'W0')}"
    if collar:
        s += f'/{collar.code}'
    return s + f'/{finish}'

def assemble_pull(bar, post, washer=None, collar=None, finish=None, name=None):
    cc = bar.meta['cc']
    t = washer.meta['t'] if washer else 0.0
    H = post.meta['H']
    sku = pull_sku(bar, post, washer, collar, finish or FINISH_DEFAULT[bar.dir])
    A = Assy(name or sku.replace('/', '_'))
    for x in (-cc / 2, cc / 2):
        side = 'L' if x < 0 else 'R'
        A.add(washer, Pos(x, 0, 0), f'w{side}')
        rot = Rot(0, 0, 90) if x > 0 and post.meta['pins'] else Rot(0, 0, 0)
        A.add(post, Pos(x, 0, t) * rot, f'p{side}')
        if collar:
            A.add(collar, Pos(x, 0, t + H), f'c{side}')
    seat = t + H + (collar.meta['f'] if collar else 0.0)
    A.add(bar, Pos(0, 0, seat), 'bar')
    A.meta = dict(kind='pull', sku=sku, cc=cc, t=t, H=H, seat=seat, land_z=t + H, bar=bar.code, post=post.code, washer=washer.code if washer else 'W0', collar=collar.code if collar else None, dir=bar.dir)
    return A

def assemble_knob(hd, stem, washer=None, finish=None, name=None):
    t = washer.meta['t'] if washer else 0.0
    H = stem.meta['H']
    sku = f"{hd.code}/{stem.code}/{(washer.code if washer else 'W0')}/{finish or FINISH_DEFAULT[hd.dir]}"
    A = Assy(name or sku.replace('/', '_'))
    A.add(washer, Pos(0, 0, 0), 'w')
    A.add(stem, Pos(0, 0, t), 's')
    A.add(hd, Pos(0, 0, t + H), 'h')
    A.meta = dict(kind='knob', sku=sku, t=t, H=H, land_z=t + H, head=hd.code, stem=stem.code, washer=washer.code if washer else 'W0', dir=hd.dir)
    return A

def _spindle(sq, z0, z1):
    sp = Pos(0, 0, (z0 + z1) / 2) * Box(sq, sq, z1 - z0)
    return Mod(f'SP{sq:g}x{z1 - z0:g}', 'spindle', 'SYS', {f'steel_SP{sq:g}': (chamfer(sp.edges().group_by(Axis.Z)[-1], 0.3), 'steel')}, {})

def assemble_door(lv, rs, escs=(), name=None, door_t=40.0):
    A = Assy(name or f'{lv.code}+{rs.code}' + ''.join(('+' + e.code for e in escs)))
    A.add(rs, Pos(0, 0, 0), 'rose')
    A.add(lv, Pos(0, 0, 0), 'lever')
    A.add(_spindle(SYS['DOOR_SPINDLE'], -rs.meta['h'] - door_t / 2, 13.5), Pos(0, 0, 0), 'spindle')
    for e in escs:
        dist = SYS['WC_DIST'] if e.meta['typ'].startswith('WC') else SYS['PZ_DIST']
        A.add(e, Pos(0, -dist - e.meta['axis'], 0), e.meta['typ'])
    A.meta = dict(kind='door', lever=lv.code, rose=rs.code, esc=[e.code for e in escs], dir=lv.dir, sku=f'{lv.code}/{rs.code}' + ''.join(('/' + e.code for e in escs)) + f'/{FINISH_DEFAULT[lv.dir]}')
    return A

def assemble_window(hd, rs, name=None):
    A = Assy(name or f'{hd.code}+{rs.code}')
    A.add(rs, Pos(0, 0, 0), 'rose')
    A.add(hd, Pos(0, 0, 0), 'handle')
    A.add(_spindle(SYS['WIN_SPINDLE'], -rs.meta['h'] - 38.0, 9.5), Pos(0, 0, 0), 'spindle')
    A.meta = dict(kind='window', handle=hd.code, rose=rs.code, dir=hd.dir, sku=f'{hd.code}/{rs.code}/{FINISH_DEFAULT[hd.dir]}')
    return A

def family_pull(dir_, cc, cache=None):
    c = cache if cache is not None else {}
    g = lambda key, fn: c.setdefault(key, fn())
    bar = g(('bar', dir_, cc), lambda: BAR_GEN[dir_](cc))
    if dir_ == 'OT':
        return assemble_pull(bar, g(('post', 'OTD', 12), lambda: make_post('OTD', 12)), g(('w', 'WD14'), lambda: make_washer('WD14')))
    if dir_ == 'PN':
        return assemble_pull(bar, g(('post', 'SQ7', 30), lambda: make_post('SQ7', 30)), g(('w', 'WS11'), lambda: make_washer('WS11')))
    if dir_ == 'KS':
        return assemble_pull(bar, g(('post', 'SK8', 30), lambda: make_post('SK8', 30)), None)
    fam = 'SR7' if cc <= 160 else 'SR8'
    if dir_ == 'OB':
        col = g(('col', bar.meta['rod_d'], bar.meta['vis_d'], 'R'), lambda: make_collar(bar.meta['rod_d'], bar.meta['vis_d'], 'R'))
        return assemble_pull(bar, g(('post', fam, 30), lambda: make_post(fam, 30)), g(('w', 'WR12'), lambda: make_washer('WR12')), col)
    col = g(('col', bar.meta['rod_d'], bar.meta['vis_d'], 'F'), lambda: make_collar(bar.meta['rod_d'], bar.meta['vis_d'], 'F'))
    return assemble_pull(bar, g(('post', 'SR8', 30), lambda: make_post('SR8', 30)), g(('w', 'WR13'), lambda: make_washer('WR13')), col)
KNOB_DEFAULT = {'OT': ('OTD-12', 'WD14'), 'PN': ('SQ7-K24', 'WS11'), 'OB': ('SR7-K21', 'WR12'), 'OS': ('SR8-K16', 'WR13'), 'KS': ('SK8-K18.5', None)}

def family_knob(dir_, size, cache=None):
    c = cache if cache is not None else {}
    st, w = KNOB_DEFAULT[dir_]
    hd = c.get(('head', dir_, size)) or c.setdefault(('head', dir_, size), head(dir_, size))
    sm = c.get(('stem', st)) or c.setdefault(('stem', st), make_stem(st))
    ws = c.get(('w', w)) or c.setdefault(('w', w), make_washer(w)) if w else None
    return assemble_knob(hd, sm, ws)

def _compound(items, label):
    ch = []
    for it in items:
        q = copy.copy(it[1])
        q.label = it[0]
        ch.append(q)
    c = Compound(children=ch)
    c.label = label
    return c

def export_mod(mod, folder):
    os.makedirs(folder, exist_ok=True)
    items = [[lab, p, m] for lab, (p, m) in mod.parts.items()]
    c = _compound(items, mod.code)
    base = os.path.join(folder, mod.code.replace('/', '_'))
    export_step(c, base + '.step')
    bb = c.bounding_box()
    return dict(code=mod.code, kind=mod.kind, dir=mod.dir, mass_g=round(mod.mass_g(), 2), bbox_mm=[round(bb.size.X, 2), round(bb.size.Y, 2), round(bb.size.Z, 2)], bodies={lab: dict(material=m, volume_mm3=round(p.volume, 1), mass_g=round(p.volume * SYS['RHO'][m], 2)) for lab, (p, m) in mod.parts.items()}, meta={k: v for k, v in mod.meta.items() if isinstance(v, (int, float, str, bool, list, tuple, type(None)))}, step=base + '.step')

def export_assy(A, folder, glb=True, step=True):
    os.makedirs(folder, exist_ok=True)
    c = _compound(A.items, A.name)
    base = os.path.join(folder, A.name)
    if step:
        export_step(c, base + '.step')
    if glb:
        export_gltf(c, base + '.glb', unit=Unit.MM, binary=True, linear_deflection=0.01, angular_deflection=0.15)
    bb = c.bounding_box()
    return dict(name=A.name, sku=A.meta.get('sku'), kind=A.meta.get('kind'), mass_g=round(A.mass_g(), 1), bbox_mm=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)], bom=A.bom(), files=[base + '.step'] * step + [base + '.glb'] * glb, meta={k: v for k, v in A.meta.items() if isinstance(v, (int, float, str, bool, list, type(None)))})

def m4_stud(L):
    s = _cyl(3.9, L, 0, 0, 0)
    s = chamfer(s.edges(), 0.3)
    s -= Pos(0, 0, L - 0.6) * Box(0.6, 2.2, 1.3)
    return Mod(f'M4x{L:g}-ISO4026', 'hw', 'SYS', {f'steel_M4x{L:g}': (s, 'steel')}, dict(L=L))

def m4_screw(L):
    sh = _cyl(3.9, L, 0, 0, 0)
    hd = rev_z([(0, -2.8), (3.5, -2.8), (3.5, -1.6), (2.0, 0), (0, 0)])
    s = chamfer(sh.edges().group_by(Axis.Z)[-1], 0.3) + hd
    return Mod(f'M4x{L:g}-ISO7380', 'hw', 'SYS', {f'steel_M4x{L:g}s': (s, 'steel')}, dict(L=L))

def joint_depths(lower, upper, collar=None):
    d_lo = SYS['POST_TAP_DEPTH'] if lower.meta['H'] >= 2 * SYS['POST_TAP_DEPTH'] + 2 else (lower.meta['H'] - SYS['CBORE_H']) / 2
    if collar is not None:
        wall = collar.meta['f'] - upper.meta['rod_d'] / 2
        return (d_lo, wall, upper.meta['tap_depth'])
    return (d_lo, 0.0, upper.meta.get('tap_depth', upper.meta.get('tap')))
STUD_LENGTHS = (8, 10, 12, 14, 16)

def pick_stud(d_lo, wall, d_up, eng_lo=None, eng_up=None):
    eng_lo = eng_lo or SYS['ENG_MIN']
    eng_up = eng_up or SYS['ENG_MIN']
    for L in STUD_LENGTHS:
        lo = min(d_lo - 0.5, L - wall - eng_up)
        up = L - wall - lo
        if lo >= eng_lo and eng_up <= up <= d_up - 0.5:
            return (L, lo, up)
    return (None, 0, 0)
