"""generate render spec JSONs for v11 (family, mix, exploded)."""
import json, sys, os
S = "/workspace/moodnook/v11/step"
R = "/workspace/moodnook/v11/renders"
os.makedirs(R, exist_ok=True); os.makedirs(R + "/spec", exist_ok=True)
PANEL = {"OT": "sand", "PN": "greige", "OB": "taupe", "OS": "greige", "KS": "sand"}


# wide knob heads (PN T-bar, OB disc) read as touching the pull post at [30,-122] -> moved clear
KNOB_LOC = {"PN": [62, -128, 0], "OB": [62, -128, 0]}


def family(D, samples=96, pct=100):
    return dict(out=f"{R}/family_{D}.png", samples=samples, res=[1600, 1200], pct=pct,
                items=[dict(glb=f"{S}/{D}/assemblies/{D}-door-PZ.glb", loc=[40, 16, 152], rot=[90, 0, 0]),
                       dict(glb=f"{S}/{D}/assemblies/{D}-pull-128.glb", loc=[-88, -40, 0], rot=[0, 0, -10]),
                       dict(glb=f"{S}/{D}/assemblies/{D}-knob-M.glb", loc=KNOB_LOC.get(D, [30, -122, 0]), rot=[0, 0, 15])],
                boxes=[dict(name="panel", size=[230, 30, 290], center=[95, 40, 145], mat=PANEL[D], bevel=1.0)],
                camera=dict(target=[8, -30, 72], dist=0.86, elev=14, azim=24, lens=85, fstop=11, focus=[-20, -60, 30]))


if __name__ == "__main__" and sys.argv[1] == "family":
    what = sys.argv[1]
    if what == "family":
        D = sys.argv[2]; sp = family(D, int(sys.argv[3]), int(sys.argv[4]))
        if len(sys.argv) > 5: sp["out"] = sys.argv[5]
        p = f"{R}/spec/family_{D}.json"; json.dump(sp, open(p, "w"), indent=1); print(p)


MIXES = [("MIX1_KS-bar_on_PN-SQ7", "pull"), ("MIX2_OB-ring_on_OS-oak", "pull"), ("MIX3_PN-fin_on_KS-SK8", "pull"),
         ("MIX4_OB-rod_on_KS-SK8", "pull"), ("MIX5_OT-pebble_on_SR8-WR12", "pull"), ("MIX6_OS-ash_on_KS-SK8", "pull"),
         ("MIX7_PN-fin_on_SR7-WT17", "pull"), ("MIX8_KS-knob_on_OB-stem", "knob"), ("MIX9_OB-knob_on_KS-stem", "knob")]


def mix_tile(name, kind, samples=64):
    cam = dict(target=[0, 0, 22], dist=0.60, elev=26, azim=32, lens=100, fstop=10) if kind == "pull" else \
        dict(target=[0, 0, 17], dist=0.36, elev=24, azim=30, lens=100, fstop=11)
    return dict(out=f"{R}/mix/{name}.png", samples=samples, res=[1000, 750],
                items=[dict(glb=f"{S}/MIX/{name}.glb", loc=[0, 0, 0], rot=[0, 0, -6 if kind == "pull" else 18])], camera=cam)


def exploded(samples=96):
    m = json.load(open(f"{R}/spec/exploded_meta.json"))
    return dict(out=f"{R}/exploded_OB-R128.png", samples=samples, res=[1600, 1200],
                items=[dict(glb=m["info"]["files"][1], loc=[0, 0, m["lift"]], rot=[0, 0, 0])],
                anchors=m["anchors"],
                camera=dict(target=[28, 0, 76], dist=0.64, elev=7, azim=14, lens=85, fstop=18))


if __name__ == "__main__" and sys.argv[1] in ("mix", "exploded"):
    os.makedirs(f"{R}/mix", exist_ok=True)
    if sys.argv[1] == "mix":
        for nm, k in MIXES:
            sp = mix_tile(nm, k, int(sys.argv[2]))
            if len(sys.argv) > 3:
                sp["pct"] = int(sys.argv[3])
            json.dump(sp, open(f"{R}/spec/{nm}.json", "w"), indent=1); print(f"{R}/spec/{nm}.json")
    else:
        sp = exploded(int(sys.argv[2]))
        if len(sys.argv) > 3:
            sp["pct"] = int(sys.argv[3]); sp["out"] = sys.argv[4]
        json.dump(sp, open(f"{R}/spec/exploded.json", "w"), indent=1); print(f"{R}/spec/exploded.json")
