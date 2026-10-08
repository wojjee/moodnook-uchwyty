"""site v12 product shots (light-stone studio, same scene.py): python3 specs_v12.py OUTDIR [samples] [pct] [filter]
writes OUTDIR/spec/<name>.json for every product hero / view; render each with
blender -b --factory-startup -P scene.py -- OUTDIR/spec/<name>.json"""
import json, sys, os
S = os.environ.get("NF_STEP", "/workspace/moodnook/v11/step")
DIRS = ["OT", "PN", "OB", "OS", "KS"]
CC = [96, 128, 160, 224, 320]


def pull_cam(cc, view="hero"):
    k = max(0.82, (cc + 40) / 168.0)
    if view == "front":
        return dict(target=[0, 0, 20], dist=0.62 * k, elev=4, azim=0, lens=100, fstop=14)
    if view == "detail":   # joint close-up: right post, washer, collar/seat
        return dict(target=[cc / 2, 0, 22], dist=0.20, elev=18, azim=34, lens=100, fstop=16)
    if view == "top":
        return dict(target=[0, 0, 10], dist=0.62 * k, elev=82, azim=0, lens=100, fstop=14)
    return dict(target=[0, 0, 21], dist=0.60 * k, elev=26, azim=32, lens=100, fstop=10)


def specs(samples=48, pct=100):
    out = {}
    W, H = 1200, 900
    for D in DIRS:
        for cc in CC:
            out[f"{D}-pull-{cc}"] = dict(samples=samples, res=[W, H], pct=pct, camera=pull_cam(cc),
                                         items=[dict(glb=f"{S}/{D}/assemblies/{D}-pull-{cc}.glb", rot=[0, 0, -6])])
        for v in ("front", "detail", "top"):
            out[f"{D}-pull-128-{v}"] = dict(samples=samples, res=[W, H], pct=pct, camera=pull_cam(128, v),
                                            items=[dict(glb=f"{S}/{D}/assemblies/{D}-pull-128.glb", rot=[0, 0, 0])])
        out[f"{D}-knob-M"] = dict(samples=samples, res=[W, H], pct=pct,
                                  camera=dict(target=[0, 0, 16], dist=0.36, elev=24, azim=30, lens=100, fstop=11),
                                  items=[dict(glb=f"{S}/{D}/assemblies/{D}-knob-M.glb", rot=[0, 0, 18])])
        out[f"{D}-knob-SML"] = dict(samples=samples, res=[W, H], pct=pct,
                                    camera=dict(target=[4, 0, 15], dist=0.47, elev=20, azim=24, lens=100, fstop=13),
                                    items=[dict(glb=f"{S}/{D}/assemblies/{D}-knob-{s}.glb", loc=[x, 0, 0], rot=[0, 0, 18])
                                           for s, x in (("S", -44), ("M", 0), ("L", 48))])
        for nm in ("door-PZ", "door-BB", "door-WC-in"):
            out[f"{D}-{nm}"] = dict(samples=samples, res=[W, H], pct=pct,
                                    camera=dict(target=[100, -20, 196], dist=0.80, elev=9, azim=20, lens=90, fstop=13),
                                    items=[dict(glb=f"{S}/{D}/assemblies/{D}-{nm}.glb", loc=[40, 16, 232], rot=[90, 0, 0])],
                                    boxes=[dict(name="panel", size=[520, 30, 620], center=[110, 40, 220], mat="sand", bevel=1.0)])
        out[f"{D}-window"] = dict(samples=samples, res=[W, H], pct=pct,
                                  camera=dict(target=[30, -20, 192], dist=0.72, elev=9, azim=22, lens=90, fstop=13),
                                  items=[dict(glb=f"{S}/{D}/assemblies/{D}-window.glb", loc=[30, 16, 230], rot=[90, 0, 0])],
                                  boxes=[dict(name="panel", size=[640, 30, 660], center=[40, 40, 220], mat="sand", bevel=1.0)])
    for cc in CC:
        out[f"OSJS-pull-{cc}"] = dict(samples=samples, res=[W, H], pct=pct, camera=pull_cam(cc),
                                      items=[dict(glb=f"{S}/OS/assemblies/OS-JS-pull-{cc}.glb", rot=[0, 0, -6])])
    return out


if __name__ == "__main__":
    od = sys.argv[1]; smp = int(sys.argv[2]) if len(sys.argv) > 2 else 48; pct = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    flt = sys.argv[4] if len(sys.argv) > 4 else ""
    os.makedirs(od + "/spec", exist_ok=True)
    n = 0
    for k, sp in specs(smp, pct).items():
        if flt and not any(f in k for f in flt.split(",")):
            continue
        sp["out"] = os.path.abspath(f"{od}/{k}.png")
        json.dump(sp, open(f"{od}/spec/{k}.json", "w"), indent=1); n += 1; print(k)
