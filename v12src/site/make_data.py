"""site v12 data: python make_data.py OUTDIR  ->  OUTDIR/v12/data.js
reads v11/test_results.json (allowed + passed combos), v11/step/*/manifest.json, OUTDIR/v12/modules.json, OUTDIR/v12/img/"""
import json, os, sys
V = os.environ.get("NF_V11", "/workspace/moodnook/v11")
OUT = sys.argv[1]
DIRS = ["OT", "PN", "OB", "OS", "KS"]
TR = json.load(open(f"{V}/test_results.json"))
MODS = json.load(open(f"{OUT}/v12/modules.json"))
MAN = {D: json.load(open(f"{V}/step/{D}/manifest.json")) for D in DIRS}
IMG = sorted(f[:-10] for f in os.listdir(f"{OUT}/v12/img") if f.endswith("-1200.webp")) if os.path.isdir(f"{OUT}/v12/img") else []
core = lambda s: s.rsplit("/", 1)[0]
assert TR["allok"], "test_results.json is not all-OK"
combos = {k: sorted({core(r["sku"]) for r in TR[k] if r["ok"]}) for k in ("pull", "knob", "door", "window")}
combos["esc"] = sorted(r["key"][0] for r in TR["esc"] if r["ok"])


def assy(D, name):
    return next(a for a in MAN[D]["assemblies"] if a["name"] == name)


def modm(D, code):
    return next(m for m in MAN[D]["modules"] if m["code"] == code)


P = []
for D in DIRS:
    for cc in (96, 128, 160, 224, 320):
        a = assy(D, f"{D}-pull-{cc}")
        views = [f"{D}-pull-128-{v}" for v in ("front", "detail", "top")]
        P.append(dict(id=f"{D}-pull-{cc}", dir=D, kind="pull", cc=cc, sku=a["sku"], mass_g=a["mass_g"], bbox=a["bbox_mm"],
                      bom=a["bom"], img=[f"{D}-pull-{cc}"] + views, meta=a["meta"]))
        if D == "OS":
            b = MODS["modules"][f"OS-JS{cc}"]
            m = dict(a["meta"]); m["bar"] = f"OS-JS{cc}"; m["washer"] = "WR13"; m["post"] = "SR8-30"
            m["collar"] = a["meta"]["collar"].replace("CR", "CF")
            sku = f"OS-JS{cc}/SR8-30/WR13/{m['collar']}/SB"
            m["sku"] = sku
            mass = round(a["mass_g"] - modm("OS", f"OS-DB{cc}")["mass_g"] + b["mass_g"], 1)
            P.append(dict(id=f"OSJS-pull-{cc}", dir=D, kind="pull", cc=cc, sku=sku, mass_g=mass, bbox=a["bbox_mm"], species="JS",
                          img=[f"OSJS-pull-{cc}"], meta=m))
    ks = {s: assy(D, f"{D}-knob-{s}") for s in "SML"}
    P.append(dict(id=f"{D}-knob", dir=D, kind="knob", sku=ks["M"]["sku"], sizes={s: dict(sku=ks[s]["sku"], mass_g=ks[s]["mass_g"], bbox=ks[s]["bbox_mm"], meta=ks[s]["meta"]) for s in "SML"},
                  mass_g=ks["M"]["mass_g"], bbox=ks["M"]["bbox_mm"], img=[f"{D}-knob-M", f"{D}-knob-SML"], meta=ks["M"]["meta"]))
    dz = assy(D, f"{D}-door-PZ")
    P.append(dict(id=f"{D}-door", dir=D, kind="door", sku=dz["sku"], mass_g=dz["mass_g"], bbox=dz["bbox_mm"],
                  lever=modm(D, f"{D}-L")["mass_g"], rose=modm(D, f"{D}-R")["mass_g"],
                  img=[f"{D}-door-PZ", f"{D}-door-BB", f"{D}-door-WC-in"], meta=dz["meta"]))
    w = assy(D, f"{D}-window")
    P.append(dict(id=f"{D}-window", dir=D, kind="window", sku=w["sku"], mass_g=w["mass_g"], bbox=w["bbox_mm"],
                  img=[f"{D}-window"], meta=w["meta"]))

MIXM = json.load(open(f"{V}/step/MIX/manifest.json"))
mix = [dict(id=a["name"], sku=a["sku"]) for a in MIXM["assemblies"] if not a["name"].startswith("MIX10")]
flex = {k: dict(delta=v["delta"], sigma=v["sigma"]) for k, v in TR["flex"].items()}
data = dict(combos=combos, counts=TR["counts"], flex=flex, arms={k: v["sigma_max"] for k, v in TR["arms"].items()},
            modules=MODS["modules"], finish_default=MODS["finish_default"], knob_default=MODS["knob_default"],
            products=P, mix=mix, images=IMG, pdf="v12/katalog-modulowy-v11.pdf")
os.makedirs(f"{OUT}/v12", exist_ok=True)
open(f"{OUT}/v12/data.js", "w").write("window.NF12=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
print("data.js", len(P), "products", {k: len(v) for k, v in combos.items()}, len(IMG), "images")
