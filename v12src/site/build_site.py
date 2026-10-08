"""assemble the v12 site: python build_site.py OUT APPDIR MODDIR(=dir with modules.json + mod/) PRODUCT_RENDERS V11_RENDERS PDF
-> OUT/index.html, OUT/v12/{app.js,app.css,data.js,modules.json,mod/*.glb,img/*-{640,1200}.webp,katalog-modulowy-v11.pdf}"""
import sys, os, shutil, glob, subprocess
from PIL import Image
OUT, APP, MODD, PR, VR, PDF = sys.argv[1:7]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(f"{OUT}/v12/img", exist_ok=True)
shutil.copy(f"{APP}/index.html", f"{OUT}/index.html")
for f in ("app.js", "app.css"):
    shutil.copy(f"{APP}/v12/{f}", f"{OUT}/v12/{f}")
shutil.copy(f"{MODD}/modules.json", f"{OUT}/v12/modules.json")
if os.path.isdir(f"{OUT}/v12/mod"):
    shutil.rmtree(f"{OUT}/v12/mod")
shutil.copytree(f"{MODD}/mod", f"{OUT}/v12/mod")
if os.path.exists(PDF):
    shutil.copy(PDF, f"{OUT}/v12/katalog-modulowy-v11.pdf")
srcs = sorted(glob.glob(f"{PR}/*.png")) + sorted(glob.glob(f"{VR}/family_*.png")) + sorted(glob.glob(f"{VR}/mix/MIX*.png")) + \
       [f"{VR}/mix_and_match_sheet.png", f"{VR}/exploded_OB-R128_annotated.png"]
n = 0
for s in srcs:
    if not os.path.exists(s) or s.endswith("_anchors.png"):
        continue
    name = os.path.basename(s)[:-4]
    im = Image.open(s).convert("RGB")
    for w in (640, 1200):
        h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(f"{OUT}/v12/img/{name}-{w}.webp", "WEBP", quality=84 if w > 700 else 80, method=6)
    n += 1
print("images", n)
subprocess.check_call([sys.executable, f"{here}/make_data.py", OUT])
