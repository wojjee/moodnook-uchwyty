# -*- coding: utf-8 -*-
"""NOOK FORM v11 — katalog modułowy (PL), public edition. HTML -> PDF/PNG via headless Chrome.
run: python3 build_pdf.py [sheets] [pdf]"""
import os, sys, json, html, subprocess, time
V = "/workspace/moodnook/v11"; R = V + "/renders"; S = V + "/step"; LAY = V + "/layout"
CHROME = "google-chrome"
e = html.escape
DIRS = ["OT", "PN", "OB", "OS", "KS"]
NAMES = {"OT": "OTOCZAK", "PN": "PION", "OB": "OBRĄCZKA", "OS": "OSIKA", "KS": "KASKADA"}
SUB = {"OT": "organiczny otoczak", "PN": "architektoniczny pion", "OB": "biżuteryjna obrączka", "OS": "skandynawska osika", "KS": "minimalny art déco"}
MAN = {D: json.load(open(f"{S}/{D}/manifest.json")) for D in DIRS}
MIXM = json.load(open(f"{S}/MIX/manifest.json"))
TR = json.load(open(f"{V}/test_results.json")) if os.path.exists(f"{V}/test_results.json") else None
EXP = json.load(open(f"{R}/spec/exploded_meta.json"))

def mod(D, code):
    for m in MAN[D]["modules"]:
        if m["code"] == code:
            return m

def assy(D, name):
    for a in MAN[D]["assemblies"]:
        if a["name"] == name:
            return a

def g(x):
    return f"{x:.0f}" if x >= 20 else f"{x:.1f}".replace(".", ",")

def num(x, d=1):
    return f"{x:.{d}f}".replace(".", ",")

CSS = """
@page { size: 297mm 210mm; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #F3EEE6; color: #2E2924; font-family: 'Jost', sans-serif; font-weight: 300; }
.serif { font-family: 'Cormorant Garamond', serif; font-weight: 300; }
.kicker { font-family: 'Jost'; font-weight: 400; letter-spacing: .3em; text-transform: uppercase; color: #8C7B66; }
img { display: block; }
section { width:297mm; height:210mm; page-break-after:always; position:relative; overflow:hidden; background:#F3EEE6; padding:16mm 20mm; }
h2 { font-size:34pt; color:#2A241F; margin:2mm 0 6mm; letter-spacing:.02em; }
h4 { font-size:7.6pt; margin:5mm 0 2mm; }
p, li { font-size:9.2pt; line-height:1.55; color:#3A332C; }
ul { padding-left:4.5mm; } li { margin-bottom:1.2mm; }
table { border-collapse:collapse; width:100%; font-size:8.2pt; line-height:1.38; }
td, th { padding:1.25mm 1.6mm 1.25mm 0; border-top:0.3mm solid #DDD3C4; vertical-align:top; text-align:left; }
th { font-weight:400; color:#8C7B66; font-size:7.2pt; letter-spacing:.12em; text-transform:uppercase; }
td.k { color:#8C7B66; font-weight:400; }
.foot { position:absolute; left:20mm; bottom:9mm; font-size:6.8pt; letter-spacing:.3em; color:#A89880; }
.pg { position:absolute; right:20mm; bottom:9mm; font-size:7pt; color:#A89880; letter-spacing:.2em; }
.c { text-align:center; } .ok { color:#5E7A4E; font-weight:400; } .no { color:#B9A688; } .def { color:#2A241F; font-weight:500; }
.note { font-size:7.6pt; color:#8C7B66; line-height:1.45; }
code { font-family:'Jost'; font-weight:400; color:#5B4A36; letter-spacing:.02em; }
"""
FOOT = "NOOK FORM · MOOD NOOK — KATALOG MODUŁOWY v11 · MOSIĄDZ BEZOŁOWIOWY CW724R · SYSTEM M4"

def page(body, n, extra_cls=""):
    return f'<section class="{extra_cls}">{body}<div class="foot">{FOOT}</div><div class="pg">{n:02d}</div></section>'

# ------------------------------------------------------------- pages ----
def p_cover():
    return f"""<section style="padding:0">
<img src="file://{R}/family_PN.png" style="position:absolute;right:0;top:0;width:178mm;height:210mm;object-fit:cover;object-position:40% 50%">
<div style="position:absolute;left:20mm;top:32mm;width:105mm">
<div class="kicker" style="font-size:9pt">NOOK FORM · Mood Nook</div>
<h1 class="serif" style="font-size:44pt;line-height:1.04;margin:10mm 0 7mm;color:#2A241F">Katalog<br>modułowy <span style="font-size:0.72em;letter-spacing:0.04em">v11</span></h1>
<div class="serif" style="font-size:17pt;font-style:italic;color:#6E604F;line-height:1.3">Pięć kierunków form,<br>jeden system M4.</div>
<p style="margin-top:12mm;font-size:9pt">OTOCZAK · PION · OBRĄCZKA · OSIKA · KASKADA<br>uchwyty 96–320 · gałki S/M/L · klamki drzwiowe · klamki okienne</p>
<p class="note" style="position:absolute;top:128mm;width:100mm">Wersja 11 · 8.10.2026 · opracowanie projektowo-techniczne. Wymiary w mm. Geometria: model parametryczny (build123d/OpenCascade), wizualizacje: render Cycles tej samej geometrii. Wszystkie dane do potwierdzenia prototypem i przez wykonawcę.</p>
</div></section>"""

def p_system(n):
    rows = [("Gwint", "M4×0,7 w każdym złączu; otwór pod gwint Ø3,3; przelot Ø4,3"),
            ("Łącznik", "trzpień bez łba M4 ISO 4026 (8–16 mm) + Loctite 243; dobór automatyczny: ≥ 4 mm wkręcenia po obu stronach"),
            ("Mocowanie do frontu", "wkręt M4×22/25/30/35 od tyłu frontu w stopę słupka"),
            ("Podkładka ↔ słupek", "czop Ø5,0 × 1,0 w kieszeni Ø5,1 × 1,2 (0,2 mm luzu osiowego – baza zawsze przylega)"),
            ("Ścianka gwintu", "≥ 1,5 mm (części toczone/frezowane); w pręcie okrągłym ≥ 1,0 mm na ≥ 4 mm"),
            ("Dno otworu", "≥ 1,0 mm mierzone na krawędzi wiertła (lico nigdy nie przebite)"),
            ("Powierzchnia styku", "≥ 10 mm² netto (≤ 120 MPa przy 1,2 kN napięcia wstępnego)"),
            ("Blokada obrotu", "kołek Ø1,0×5 ISO 8734 na przekątnej r 3,25 – słupki kwadratowe i gałka T"),
            ("Prześwit pod chwytem", "≥ 30 mm (uchwyty), ≥ 15 mm (pod głowicą gałki)"),
            ("Sztywność", "100 N w środku: ugięcie ≤ 0,5 mm, naprężenie ≤ 150 MPa (E 95 GPa)")]
    t = "".join(f"<tr><td class='k' style='width:36mm'>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in rows)
    seats = [("F – płaska baza", "PION (FIN), KASKADA, gałka T", "gwinty w osiach ±CC/2, otwory kołków dla SQ7"),
             ("C – pręt przez obrączkę", "OBRĄCZKA, OSIKA", "obrączka 6 mm z płaską bazą ≥ 5,6 mm jest złączem"),
             ("W – talia", "OTOCZAK OT-M", "czop odlewu kończy się płaskim czołem Ø7,2 – 19 mm pod chwytem")]
    ts = "".join(f"<tr><td class='def'>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td></tr>" for a, b, c in seats)
    return page(f"""
<div class="kicker">01 · Architektura</div><h2 class="serif">Jedno złącze dla wszystkich form</h2>
<div style="display:flex;gap:10mm">
<div style="flex:1.05">
<p>Każdy kierunek to tylko <i>język formy</i> nałożony na te same interfejsy. Chwyt, obrączka, słupek, podkładka i głowica gałki łączą się zawsze tak samo: dwa gwinty wewnętrzne M4 i trzpień między nimi – każdy moduł spełniający reguły pasuje do każdego innego.</p>
<h4 class="kicker">Parametry złącza</h4><table style="font-size:7.8pt">{t}</table>
</div>
<div style="flex:1;position:relative"><img src="file://{LAY}/exploded_crop.png" style="width:100%;margin-top:-8mm">
<h4 class="kicker" style="margin-top:2mm">Trzy typy osadzenia chwytu</h4><table style="font-size:7.8pt"><tr><th>Typ</th><th>Kierunki</th><th>Interfejs</th></tr>{ts}</table></div>
</div>""", n)

def p_material(n):
    fin = [("SB", "satyna (szczotkowany)", "bez powłoki – żywy, patynuje", "tak*"), ("PB", "polerowany", "bez powłoki", "tak*"),
           ("AB", "postarzany (patyna chem. + wosk)", "bez powłoki (wosk)", "tak*"), ("MB", "czarny mat", "powłoka PVD / e-coat", "nie"),
           ("WH", "ciepła biel", "powłoka proszkowa/ceramiczna", "nie"), ("NK", "nikiel szczotkowany", "galwaniczna", "nie")]
    tf = "".join(f"<tr><td class='def'>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in fin)
    return page(f"""
<div class="kicker">02 · Materiał i wykończenia</div><h2 class="serif">Mosiądz bezołowiowy CW724R</h2>
<div style="display:flex;gap:12mm"><div style="flex:1">
<table>
<tr><td class="k" style="width:40mm">Gatunek</td><td><b>CW724R (CuZn21Si3P)</b> – bezołowiowy (Pb ≤ 0,10 %), zgodny z RoHS/REACH, lista pozytywna 4MS. <b>Nie</b> CW614N / CW617N.</td></tr>
<tr><td class="k">Gęstość</td><td>8,28 g/cm³ (wszystkie masy w katalogu)</td></tr>
<tr><td class="k">Moduł Younga</td><td>≈ 95 GPa (wartość obliczeniowa)</td></tr>
<tr><td class="k">Rp0,2</td><td>≥ 300–400 MPa (pręt ciągniony, wg średnicy)</td></tr>
<tr><td class="k">Skrawalność</td><td>ok. 80 % CuZn39Pb3 – ostre narzędzia, chłodziwo; M4 gwintuje się dobrze</td></tr>
<tr><td class="k">Cu</td><td>ok. 76 % → miedziowe właściwości powierzchni zachowane</td></tr>
<tr><td class="k">Drewno (OSIKA)</td><td>dąb (DB) lub jesion (JS), olej-wosk; klejone epoksydem na rdzeń, dzielone pod obrączkami (bez widocznych czół)</td></tr>
<tr><td class="k">Odlew (OTOCZAK)</td><td>wosk tracony w CW724R lub odpowiedniku odlewniczym bezołowiowym; czoło Ø7,2 i gwinty obrabiane po odlewie</td></tr>
</table></div>
<div style="flex:1"><h4 class="kicker" style="margin-top:0">Wykończenia – ostatnie pole SKU</h4>
<table><tr><th>Kod</th><th>Wykończenie</th><th>Powłoka</th><th>Antybakt.</th></tr>{tf}</table>
<p class="note" style="margin-top:3mm">* Komunikat o właściwościach antybakteryjnych tylko dla niepowlekanego mosiądzu (Cu ≥ 60 %). To deklaracja w rozumieniu BPR (UE) 528/2012 – wymaga badań własnych próbek SB/PB/AB (np. ISO 22196 / JIS Z 2801) i weryfikacji prawnej przed użyciem. Przy MB/WH/NK maskujemy gwinty, czopy i kieszenie. Akcent zapisujemy kropką: <code>SB.PB</code> = korpus satyna, pierścienie poler. Na jednym uchwycie nie łączymy części powlekanych z niepowlekanymi.</p>
</div></div>""", n)

MATRIX_POST = [("OTD-12", ["●", "–", "–", "–", "–"]), ("SR7-12", ["✓", "–", "–", "–", "–"]), ("SR8-12", ["✓", "–", "–", "–", "–"]),
               ("SK8-12", ["✓", "–", "–", "–", "–"]), ("SR7-30", ["–", "✓", "● ≤160", "✓", "✓"]), ("SR8-30", ["–", "✓", "● 224/320", "●", "✓"]),
               ("SQ7-30", ["–", "●", "–", "–", "✓"]), ("SK8-30", ["–", "✓", "✓", "✓", "●"])]
MATRIX_W = [("W0", "✓ ✓ ✓ ● ✓"), ("WR12 Ø12 PB", "● ✓ – – ✓"), ("WR13 Ø13", "✓ ● – – ✓"), ("WD14 kopułka", "✓ ✓ – – ●"),
            ("WS11 □11", "✓ ✓ ● – ✓"), ("WT17 schodkowa", "✓ ✓ – – ✓")]
MATRIX_K = [("OT-K S/M/L", "● ✓ – – – –"), ("PN-K S/M/L", "– – – – – ●"), ("OB-K S/M/L", "– – ● ✓ ✓ ✓"),
            ("OS-K S/M/L", "– – ✓ ● ✓ ✓"), ("KS-K S/M/L", "– – ✓ ✓ ● ✓")]

def cell(x):
    cls = "def" if x.startswith("●") else ("ok" if x.startswith("✓") else "no")
    return f"<td class='c {cls}'>{e(x)}</td>"

def p_matrix(n):
    t1 = "".join(f"<tr><td class='def'>{a}</td>{''.join(cell(x) for x in r)}</tr>" for a, r in MATRIX_POST)
    t2 = "".join(f"<tr><td class='def'>{a}</td>{''.join(cell(x) for x in r.split())}</tr>" for a, r in MATRIX_W)
    t3 = "".join(f"<tr><td class='def'>{a}</td>{''.join(cell(x) for x in r.split())}</tr>" for a, r in MATRIX_K)
    col = [("CR8-8 / CF8-8", "8", "8", "11,5", "OB 96–224"), ("CR10-10 / CF10-10", "10", "10", "13,3", "OB 320"),
           ("CR8-12 / CF8-12", "8", "12", "13,3", "OS 96–160"), ("CR8-13 / CF8-13", "8", "13", "14,2", "OS 224"), ("CR10-15 / CF10-15", "10", "15", "16,1", "OS 320")]
    t4 = "".join(f"<tr><td class='def'>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{f}</td></tr>" for a, b, c, d, f in col)
    cnt = ""
    if TR:
        c = TR["counts"]
        cnt = f"Test systemu: {c['pull']['total']} kombinacji uchwytów, {c['knob']['total']} gałek, {c['door']['total']} klamek × rozet, {c['window']['total']} klamek okiennych × rozet – wszystkie złożone i sprawdzone geometrycznie."
    return page(f"""
<div class="kicker">03 · Macierz modułów</div><h2 class="serif">Co z czym się łączy</h2>
<div style="display:flex;gap:9mm">
<div style="flex:1.1"><h4 class="kicker" style="margin-top:0">Słupek × chwyt (typ osadzenia)</h4>
<table><tr><th>Słupek</th><th class="c">OT (W)</th><th class="c">PN (F)</th><th class="c">OB (C)</th><th class="c">OS (C)</th><th class="c">KS (F)</th></tr>{t1}</table>
<h4 class="kicker">Obrączki / tulejki (osadzenie C) · szer. 6,0</h4>
<table><tr><th>Kod</th><th>Pręt Ø</th><th>Widoczne Ø</th><th>Ø obrączki</th><th>Zastosowanie</th></tr>{t4}</table>
<p class="note" style="margin-top:2mm">CR = obrączka OBRĄCZKI (PB, zaokrąglone krawędzie R1,2), CF = tulejka OSIKI (SB, faza 0,3). Para (pręt, widoczne Ø) musi zgadzać się z chwytem – styl R/F jest dowolny; tak powstaje np. polerowana obrączka na dębowej OSICE.</p>
</div>
<div style="flex:1"><h4 class="kicker" style="margin-top:0">Podkładka × słupek</h4>
<table><tr><th>Podkładka</th><th class="c">SR7</th><th class="c">SR8</th><th class="c">SQ7</th><th class="c">SK8</th><th class="c">OTD</th></tr>{t2}</table>
<h4 class="kicker">Głowica gałki × trzon</h4>
<table><tr><th>Głowica</th><th class="c">OTD-12</th><th class="c">SR8-12</th><th class="c">SR7-K21</th><th class="c">SR8-K16</th><th class="c">SK8-K18,5</th><th class="c">SQ7-K24</th></tr>{t3}</table>
<p class="note" style="margin-top:3mm">● domyślne w rodzinie · ✓ dozwolone i przetestowane · – niedozwolone. Reguły: SQ7 tylko pod chwytami F (kołek), SK8 bez podkładki (stopa schodkowa w komplecie), OTD tylko pod OTOCZAKIEM, gałka T PIONU tylko na trzonie z kołkiem SQ7-K24. Klamki: każda klamka na każdej rozecie (wspólny czop Ø15 / □8). {e(cnt)}</p>
</div></div>""", n)

FAM = {
 "OT": dict(desc="Organiczny, wypolerowany przez wodę kształt. Chwyt-otoczak to jeden odlew z kroplowymi czopami; wymiana nóżek odbywa się w najwęższym miejscu – talii Ø7,2, 19 mm pod chwytem – więc złącze jest niewidoczne, a system pozostaje modułowy.",
            sect="superelipsa n 2,4: 14,6 × 8,5 (≤160), 16 × 9,4 (224/320)", posts="OTD-12 (kropla Ø8,4 → Ø7,2) + WD14", knob="owalna głowica + czop do talii; trzon OTD-12 (ten sam co w uchwycie)",
            lever="ramię-otoczak 18 × 11, szyjka wtopiona R3; rozeta kopułkowa Ø52 × 9", win="ramię-otoczak 110; rozeta 29 × 72 × 12, narożniki R8, góra R5"),
 "PN": dict(desc="Architektoniczny, pionowy przekrój jak płetwa. Czyste płaszczyzny, mikrofazy 0,25–0,35, kwadratowe słupki z kołkiem ustalającym – wszystko w osi pionu.",
            sect="FIN 7 × 12 (320: 8 × 14)", posts="SQ7-30 + WS11 (kołek Ø1 blokuje obrót)", knob="T-bar 26/32/40 × 7 × 12 na SQ7-K24 z kołkiem",
            lever="FIN 8 × 16, szyjka □18; rozeta □50 × 9", win="FIN, rozeta 29 × 72 × 12 faza 0,6"),
 "OB": dict(desc="Biżuteria mebla: matowy pręt i cienkie, polerowane obrączki. W v11 obrączka jest jednocześnie złączem – ma płaską bazę i przelot M4, dzięki czemu pręt staje się modułowy, a obrączki można przenosić na inne kierunki.",
            sect="pręt Ø8 (320: Ø10), mat, kopułkowe końce", posts="SR7-30 (224/320: SR8-30) + WR12 PB + CR8-8", knob="tarcza Ø24/28/34 × 5,5 mat + polerowany bezel; SR7-K21",
            lever="pręt Ø16 mat + pierścień PB przy szyjce; rozeta Ø49 mat + obrzeże PB Ø52", win="rozeta zaokrąglona R6 z polerowanym pierścieniem-inkrustacją"),
 "OS": dict(desc="Skandynawskie ciepło: mosiężny rdzeń w tulei z dębu lub jesionu, satynowe tulejki w miejscu nóżek. Drewno dzielone na trzy segmenty dokładnie pod tulejkami – nigdzie nie widać czoła drewna.",
            sect="rdzeń Ø8 + dąb/jesion Ø12 (224: 8+13, 320: 10+15)", posts="SR8-30 + WR13 + CF8-12", knob="kopułka dębowa Ø25/30/35 na mosiężnej bazie z tuleją M4; SR8-K16",
            lever="rdzeń Ø12 + dąb Ø20 + nasadka; rozeta Ø52 × 9 z dębowym pierścieniem", win="rozeta 29 × 72 × 12 R3, faza 0,3"),
 "KS": dict(desc="Minimalne art déco: schodki w przekroju, w nóżkach, rozetach i gałce. Ten sam rytm stopni (3 + 3 + 3) powtarza się w każdym elemencie rodziny.",
            sect="dwa stopnie 11 × 3,5 + 6,6 × 3,5 (320: S320L 13 × 4,2 + 8 × 4,2)", posts="SK8-30 – schodkowa stopa Ø13/10,5 zintegrowana, bez podkładki", knob="trzy stopnie D / 0,84D / 0,68D; SK8-K18,5",
            lever="dwa stopnie 14 + 9 × 4 + 4, szyjka schodkowa Ø24/19/15; rozeta Ø52/44/36", win="rozeta trzystopniowa 29×72 / 23×66 / 17×60"),
}

def p_family(D, n):
    f = FAM[D]
    rows = []
    for cc in (96, 128, 160, 224, 320):
        a = assy(D, f"{D}-pull-{cc}")
        bar = [m for m in MAN[D]["modules"] if m["kind"] == "bar" and str(cc) in m["code"] and "-JS" not in m["code"]][0]
        fl = TR["flex"].get(bar["code"], {}) if TR else {}
        Lb = bar["bbox_mm"][0]
        rows.append(f"<tr><td class='def'>{cc}</td><td>{num(Lb, 1)}</td><td>{g(bar['mass_g'])}</td><td>{g(a['mass_g'])}</td>"
                    f"<td>{num(fl.get('delta', 0), 2)}</td><td><code>{e(a['sku'])}</code></td></tr>")
    krows = []
    for s in "SML":
        a = assy(D, f"{D}-knob-{s}")
        h = mod(D, f"{D}-K{s}")
        bbx = h["bbox_mm"]
        kc = ""
        if TR:
            kk = [r for r in TR["knob"] if r["sku"] == a["sku"]]
            kc = num(kk[0]["metrics"].get("clearance", 0), 1) if kk else ""
        krows.append(f"<tr><td class='def'>{s}</td><td>{num(bbx[0], 1)} × {num(bbx[1], 1)} × {num(bbx[2], 1)}</td><td>{g(a['mass_g'])}</td><td>{kc}</td><td><code>{e(a['sku'])}</code></td></tr>")
    lv, rs = mod(D, f"{D}-L"), mod(D, f"{D}-R")
    wh, wr = mod(D, f"{D}-O"), mod(D, f"{D}-RO")
    arm = TR["arms"].get(f"{D}-L", {}).get("sigma_max", "") if TR else ""
    arm2 = TR["arms"].get(f"{D}-O", {}).get("sigma_max", "") if TR else ""
    return page(f"""
<div style="display:flex;gap:9mm;height:176mm">
<div style="flex:1.12">
<div class="kicker">Rodzina · {e(SUB[D])}</div><h2 class="serif" style="font-size:38pt;margin-bottom:3mm">{e(NAMES[D])} <span style="font-size:16pt;color:#8C7B66">{D}</span></h2>
<img src="file://{R}/family_{D}.png" style="width:100%;height:auto">
<p style="margin-top:3mm">{e(f['desc'])}</p>
</div>
<div style="flex:1;padding-top:3mm">
<table><tr><td class="k" style="width:28mm">Przekrój chwytu</td><td>{e(f['sect'])}</td></tr>
<tr><td class="k">Słupki</td><td>{e(f['posts'])}</td></tr><tr><td class="k">Gałka</td><td>{e(f['knob'])}</td></tr>
<tr><td class="k">Klamka drzwiowa</td><td>{e(f['lever'])} · {g(lv['mass_g'])} g + rozeta {g(rs['mass_g'])} g · σ ramienia {arm} MPa @200 N</td></tr>
<tr><td class="k">Klamka okienna</td><td>{e(f['win'])} · {g(wh['mass_g'])} g + rozeta {g(wr['mass_g'])} g · σ {arm2} MPa</td></tr></table>
<h4 class="kicker">Uchwyty – rozstawy</h4>
<table><tr><th>CC</th><th>L</th><th>chwyt [g]</th><th>komplet [g]</th><th>δ 100 N</th><th>SKU (domyślne)</th></tr>{''.join(rows)}</table>
<h4 class="kicker">Gałki</h4>
<table><tr><th></th><th>głowica [mm]</th><th>[g]</th><th>prześwit</th><th>SKU</th></tr>{''.join(krows)}</table>
<p class="note" style="margin-top:2mm">Masy z modelu CAD (CW724R 8,28 g/cm³; dąb 0,70), komplet = chwyt + 2 słupki + podkładki/obrączki, bez wkrętów. δ = ugięcie przy 100 N w środku (utwierdzenie obustronne, sam mosiądz).</p>
</div></div>""", n)

MIX_TXT = {
 "MIX1_KS-bar_on_PN-SQ7": "KASKADA na słupkach PION",
 "MIX2_OB-ring_on_OS-oak": "Obrączki PB na dębowej OSICE",
 "MIX3_PN-fin_on_KS-SK8": "PION na schodkowych słupkach KASKADY",
 "MIX4_OB-rod_on_KS-SK8": "OBRĄCZKA na słupkach KASKADY",
 "MIX5_OT-pebble_on_SR8-WR12": "OTOCZAK na słupkach SR8 + podkładka PB",
 "MIX6_OS-ash_on_KS-SK8": "OSIKA jesion na słupkach KASKADY",
 "MIX7_PN-fin_on_SR7-WT17": "PION na okrągłych słupkach + podkładka schodkowa",
 "MIX8_KS-knob_on_OB-stem": "Gałka KASKADA na trzonie OBRĄCZKI",
 "MIX9_OB-knob_on_KS-stem": "Gałka OBRĄCZKA na trzonie KASKADY",
}

def mix_sheet_html(W=2970, H=2100):
    sk = {a["name"]: a["sku"] for a in MIXM["assemblies"]}
    cells = "".join(f"""<div class="t"><img src="file://{R}/mix/{k}.png"><div class="n serif">{e(v)}</div><div class="s">{e(sk.get(k, ''))}</div></div>""" for k, v in MIX_TXT.items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body {{ width:{W}px; height:{H}px; overflow:hidden; padding:100px 130px; }}
h1 {{ font-size:84px; color:#2A241F; }} .top {{ display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:46px; }}
.g {{ display:grid; grid-template-columns:repeat(3, 1fr); gap:26px 34px; }}
.t img {{ width:100%; aspect-ratio:1.9; object-fit:cover; object-position:50% 55%; }}
.n {{ font-size:34px; margin-top:12px; color:#2A241F; }} .s {{ font-size:19px; letter-spacing:.06em; color:#8C7B66; margin-top:4px; }}
</style></head><body><div class="top"><h1 class="serif">Mix &amp; match</h1><div class="kicker" style="font-size:20px">Moduły różnych kierunków · ten sam system M4 · wszystkie kombinacje przetestowane</div></div>
<div class="g">{cells}</div></body></html>"""

def exploded_html(W=1600, H=1200):
    an = json.load(open(f"{R}/exploded_OB-R128_anchors.json"))
    lab = EXP["labels"]
    order = ["bar", "collar", "stud", "post", "washer", "screw"]
    items = ""
    import re as _re
    lab = {k: (t, _re.sub(r"(?<=\d)\.(?=\d)", ",", s).replace("satynowy-mat", "satyna SB").replace("mosiądz satyna SB, 2× M4 gwint promieniowy (gł. 6,59)", "satyna SB, 2× M4, gł. 6,6")) for k, (t, s) in lab.items()}
    # bar: lead from the end cap, not along the rod (anchor projected from the bar mid-point)
    cx = an["collar"][0]
    an = dict(an); an["bar"] = [cx + 72, an["bar"][1] + 8]
    for k in order:
        x, y = an[k]
        lx = 1150
        t, s = lab[k]
        items += f"""<div style="position:absolute;left:{x}px;top:{y}px;width:{lx - x - 14}px;height:0;border-top:1.4px solid #A08C70"></div>
<div style="position:absolute;left:{x - 4}px;top:{y - 4}px;width:8px;height:8px;border-radius:4px;background:#A08C70"></div>
<div style="position:absolute;left:{lx}px;top:{y - 26}px;width:420px"><div class="serif" style="font-size:36px;line-height:1.05;color:#2A241F;font-weight:400">{e(t)}</div>
<div style="font-size:20px;color:#6A5A45;line-height:1.3;margin-top:3px">{e(s)}</div></div>"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS} body {{ width:{W}px;height:{H}px;position:relative;overflow:hidden; }}</style></head>
<body><img src="file://{R}/exploded_OB-R128.png" style="position:absolute;left:0;top:0;width:{W}px;height:{H}px">
<div class="kicker" style="position:absolute;left:60px;top:54px;font-size:16px">Widok rozstrzelony · OB-R128 / SR7-30 / WR12 / CR8-8 / SB.PB</div>{items}</body></html>"""

def p_mix(n):
    return page(f"""<div class="kicker">09 · Mix &amp; match</div><h2 class="serif" style="margin-bottom:3mm">Kierunki można łączyć</h2>
<img src="file://{R}/mix_and_match_sheet.png" style="width:auto;height:136mm;margin:0 auto">""", n)

def p_sku(n):
    ex = [("PN-F128/SQ7-30/WS11/SB", "PION 128, słupki kwadratowe, podkładki kwadratowe, satyna"),
          ("KS-S128/SQ7-30/WS11/SB", "chwyt KASKADA na słupkach PION (mix)"),
          ("OS-DB128/SR8-30/WR12/CR8-12/SB.PB", "OSIKA dąb z polerowanymi obrączkami OBRĄCZKI (mix)"),
          ("OT-G160/OTD-12/WD14/AB", "OTOCZAK 160, postarzany"),
          ("OB-KM/SR7-K21/WR12/SB.PB", "gałka OBRĄCZKA M"),
          ("KS-L/KS-R/KS-EPZ/SB", "klamka KASKADA na rozecie + szyld PZ"),
          ("PN-O/PN-RO/MB", "klamka okienna PION, czarny mat")]
    te = "".join(f"<tr><td><code>{e(a)}</code></td><td>{e(b)}</td></tr>" for a, b in ex)
    return page(f"""
<div class="kicker">10 · Kody produktów</div><h2 class="serif">Schemat SKU</h2>
<div style="display:flex;gap:12mm"><div style="flex:1">
<table>
<tr><td class="k" style="width:28mm">UCHWYT</td><td><code>{{KIER}}-{{typ}}{{CC}} / {{słupek}}-{{H}} / {{podkładka}} [/ {{obrączka}}] / {{wykończenie}}</code></td></tr>
<tr><td class="k">GAŁKA</td><td><code>{{KIER}}-K{{S|M|L}} / {{trzon}} / {{podkładka}} / {{wykończenie}}</code></td></tr>
<tr><td class="k">DRZWI</td><td><code>{{KIER}}-L / {{KIER}}-R / {{KIER}}-E{{PZ|BB|WCi|WCo}} / {{wykończenie}}</code></td></tr>
<tr><td class="k">OKNO</td><td><code>{{KIER}}-O / {{KIER}}-RO / {{wykończenie}}</code></td></tr></table>
<h4 class="kicker">Pola</h4><table>
<tr><td class="k" style="width:28mm">KIER</td><td>OT · PN · OB · OS · KS</td></tr>
<tr><td class="k">typ</td><td>G otoczak · F płetwa · R pręt · DB/JS dąb/jesion · S schodki (S320L wzmocniony)</td></tr>
<tr><td class="k">słupek</td><td>SR7 · SR8 · SQ7 · SK8 · OTD + wysokość (12 / 30); trzony gałek SR7-K21 · SR8-K16 · SQ7-K24 · SK8-K18.5</td></tr>
<tr><td class="k">podkładka</td><td>W0 · WR12 · WR13 · WD14 · WS11 · WT17</td></tr>
<tr><td class="k">obrączka</td><td>CR{{pręt}}-{{widoczne}} (obrączka PB) · CF{{pręt}}-{{widoczne}} (tulejka SB)</td></tr>
<tr><td class="k">wykończenie</td><td>SB · PB · AB · MB · WH · NK; akcent po kropce: SB.PB</td></tr></table>
</div><div style="flex:1"><h4 class="kicker" style="margin-top:0">Przykłady</h4><table>{te}</table>
<p style="margin-top:5mm">Każdy moduł ma też własny kod części zamiennej (<code>SQ7-30/SB</code>, <code>CR8-12/PB</code>, <code>M4x10-ISO4026</code>). Klient może więc po latach „przebrać” uchwyty – zmienić słupki, podkładki lub obrączki bez nowych otworów w meblu.</p>
</div></div>""", n)

def p_standards(n):
    return page(f"""
<div class="kicker">11 · Normy UE</div><h2 class="serif">Klamki drzwiowe i okienne</h2>
<div style="display:flex;gap:11mm"><div style="flex:1">
<h4 class="kicker" style="margin-top:0">Drzwi wewnętrzne</h4><table>
<tr><td class="k" style="width:34mm">Trzpień</td><td>□8 mm (opcja □9 do zestawów ppoż./antywłamaniowych)</td></tr>
<tr><td class="k">Łożyskowanie</td><td>czop klamki Ø15 × 4 w otworze rozety Ø15,2; wkręt dociskowy M4 od spodu szyjki – niewidoczny (Ø12 odrzucono – 0,35 mm ścianki w narożach □8)</td></tr>
<tr><td class="k">Rozeta</td><td>mosiężna nakładka na kupną stalową bazę z kasetą sprężyny powrotnej; 2 × M4 przelotowe, niewidoczne; Ø52 × 9 (PION □50 × 9)</td></tr>
<tr><td class="k">Szyldy</td><td>ten sam obrys co rozeta. PZ – wkładka profilowa EN 1303 (Ø17 + 10, 33 mm) w rozstawie <b>72 mm</b>; BB – klucz zwykły, <b>72 mm</b>; WC – pokrętło wewnątrz / zwolnienie awaryjne na zewnątrz, <b>78 mm</b> (DIN 18251)</td></tr>
<tr><td class="k">Geometria</td><td>ramię 132 mm, oś ramienia ok. 55 mm od skrzydła</td></tr>
<tr><td class="k">Norma</td><td><b>EN 1906</b> – klasyfikacja 8-cyfrowa. Cel: <b>3 7 – 0 1 4 0 A</b> (kat. użytkowania 3, trwałość 7 = 200 000 cykli, ogień 0, bezpieczeństwo 1, korozja 4 wg EN 1670, włamanie 0, A = klamka wspomagana sprężyną)</td></tr></table>
</div><div style="flex:1">
<h4 class="kicker" style="margin-top:0">Okna rozwierno-uchylne</h4><table>
<tr><td class="k" style="width:34mm">Trzpień</td><td>□7 mm, standard 7 × 38 (opcje 30–45)</td></tr>
<tr><td class="k">Mocowanie</td><td><b>2 × M5 w rozstawie 43 mm</b> (DIN 18267) – świadomy wyjątek od zasady „M4 wszędzie”, bo to rynkowy interfejs okuć; złącza mosiężne wewnątrz pozostają M4</td></tr>
<tr><td class="k">Rozeta</td><td>ok. 29 × 72 × 12 w języku kierunku, na stalowej płytce; wkręty ukryte pod nakładką</td></tr>
<tr><td class="k">Klamka</td><td>ramię 110 mm, wysięg ok. 50–57 mm, zapadka 4 × 90° z kupnej wkładki</td></tr>
<tr><td class="k">Norma</td><td><b>EN 13126-3</b> (klamki okienne), wymiary DIN 18267</td></tr></table>
<h4 class="kicker">Wstępna weryfikacja w modelu</h4>
<p>Każda klamka na każdej rozecie (wspólny czop): kolizje = 0, styk barku z rozetą, przejście trzpienia i wkrętu dociskowego, odległości 72/78, M5 co 43 mm ukryte pod nakładką, naprężenie u nasady ramienia przy 200 N ≤ 200 MPa. To tylko filtr projektowy – klasyfikacja EN 1906 / EN 13126-3 wymaga badań w akredytowanym laboratorium.</p>
</div></div>""", n)

def p_tests(n):
    if not TR:
        return ""
    c = TR["counts"]
    rows = [("Uchwyty (chwyt × słupek × podkładka × obrączka, 5 rozstawów)", c["pull"]), ("Gałki (głowica S/M/L × trzon × podkładka)", c["knob"]),
            ("Klamka × rozeta drzwiowa (każda z każdą)", c["door"]), ("Klamka okienna × rozeta okienna", c["window"]), ("Szyldy PZ/BB/WC – 5 kierunków", c["esc"])]
    t = "".join(f"<tr><td>{e(a)}</td><td class='c'>{b['total']}</td><td class='c ok'>{b['passed']}</td></tr>" for a, b in rows)
    tot = sum(b["total"] for _, b in rows); pas = sum(b["passed"] for _, b in rows)
    dirrows = ""
    for D in DIRS:
        rr = [r for r in TR["pull"] if r["key"][0] == D]
        dirrows += (f"<tr><td class='def'>{NAMES[D]}</td><td class='c'>{len(rr)}</td><td class='c'>{num(min(r['metrics']['clearance'] for r in rr), 1)} mm</td>"
                    f"<td class='c'>{num(max(r['metrics']['delta'] for r in rr), 2)} mm</td><td class='c'>{max(r['metrics']['sigma'] for r in rr):.0f} MPa</td></tr>")
    PLN = {"v10 OBRĄCZKA rod Ø9 @320 (flex)": "OBRĄCZKA 320 z prętem Ø9 jak w v10 – ugięcie",
           "KASKADA standard section @320 (flex)": "KASKADA 320 w przekroju standardowym – ugięcie",
           "PION fin on 24 mm posts (clearance)": "PION na słupkach 24 mm – prześwit",
           "square post under a collar (no pin hole)": "słupek kwadratowy pod obrączką – brak gniazda kołka",
           "OB ring collar CR8-8 on OSIKA Ø12 sleeve (mismatch)": "obrączka CR8-8 na tulei OSIKI Ø12 – niezgodna para",
           "PION T-knob on round stem (no anti-rotation)": "gałka T PIONU na okrągłym trzonie – brak blokady obrotu",
           "OB knob on a 10 mm stem (under-head clearance)": "gałka OBRĄCZKA na trzonie 10 mm – prześwit pod głowicą",
           "OTOCZAK pebble on 10 mm posts (clearance)": "OTOCZAK na słupkach 10 mm – prześwit / wkręcenie",
           "v10 Ø7 rod with M4 radial thread (roof/engagement)": "pręt Ø7 z v10 z gwintem M4 – ścianka gwintu",
           "lever with Ø10 brass core in oak (arm stress)": "klamka z rdzeniem Ø10 w dębie – naprężenie"}
    neg = "".join(f"<tr><td>{e(PLN.get(r['name'], r['name']))}</td><td class='{'ok' if r['caught'] else 'no'}'>{'odrzucone' if r['caught'] else 'NIE'}</td></tr>" for r in TR["negative"])
    return page(f"""
<div class="kicker">12 · Weryfikacja</div><h2 class="serif">Test całego systemu</h2>
<div style="display:flex;gap:11mm"><div style="flex:1.1">
<p>Test systemu składa <b>każdą dozwoloną kombinację</b> z rzeczywistej geometrii B-rep i sprawdza: zgodność interfejsów (osie M4, czop/kieszeń, kołki, para pręt/obrączka), brak kolizji i styk ≥ 10 mm², ściankę gwintu (pierścieniowe sondy wokół każdego otworu), dno otworu, długość wkręcenia ze standardowym trzpieniem, prześwit ≥ 30 mm / ≥ 15 mm, ugięcie przy 100 N, a dla klamek – trzpienie, rozstawy i naprężenia.</p>
<table style="margin-top:4mm"><tr><th>Grupa</th><th class="c">kombinacje</th><th class="c">zaliczone</th></tr>{t}
<tr><td class="def">Razem</td><td class="c def">{tot}</td><td class="c ok">{pas}</td></tr></table>
<h4 class="kicker">Uchwyty wg kierunku</h4><table><tr><th>Kierunek</th><th class="c">kombinacje</th><th class="c">min. prześwit</th><th class="c">maks. δ 100 N</th><th class="c">maks. σ</th></tr>{dirrows}</table>
<p class="note" style="margin-top:3mm">Losowe {c['spot']['total']} kombinacji przeliczono ponownie bez pamięci podręcznej – wyniki identyczne ({c['spot']['agree']}/{c['spot']['total']}).</p>
</div><div style="flex:1"><h4 class="kicker" style="margin-top:0">Testy negatywne – znane błędy muszą zostać wykryte</h4>
<table>{neg}</table>
<p class="note" style="margin-top:3mm">Wnioski z testów, wprowadzone w v11: pręt OBRĄCZKI/rdzeń OSIKI Ø7 → Ø8 (w Ø7 dno otworu M4 tylko 0,79 mm na krawędzi wiertła); OBRĄCZKA 320 Ø9 → Ø10 (ugięcie 0,56 → 0,3 mm); KASKADA 320 przekrój wzmocniony S320L; OTOCZAK talia 19 mm pod chwytem; gałki OTOCZAKA na słupkach H12 (H10 za krótkie na wspólny gwint).</p>
</div></div>""", n)

def shot(htmlfile, png, W, H):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={W},{H}", "--force-device-scale-factor=1", "--virtual-time-budget=4000", f"--screenshot={png}", "file://" + htmlfile],
                   check=True, capture_output=True)

if __name__ == "__main__":
    what = sys.argv[1:] or ["sheets", "pdf"]
    if "sheets" in what:
        f = f"{LAY}/mix.html"; open(f, "w").write(mix_sheet_html()); shot(f, f"{R}/mix_and_match_sheet.png", 2970, 2100); print("mix sheet")
        f = f"{LAY}/exploded.html"; open(f, "w").write(exploded_html()); shot(f, f"{R}/exploded_OB-R128_annotated.png", 1600, 1200); print("exploded")
        from PIL import Image   # tighter crop for the A4 page (empty studio margin removed)
        Image.open(f"{R}/exploded_OB-R128_annotated.png").crop((150, 120, 1600, 1110)).save(f"{LAY}/exploded_crop.png")
    if "pdf" in what:
        pages = [p_cover(), p_system(1), p_material(2), p_matrix(3)]
        for i, D in enumerate(DIRS):
            pages.append(p_family(D, 4 + i))
        pages += [p_mix(9), p_sku(10), p_standards(11), p_tests(12)]  # public edition: internal prototyping plan omitted
        doc = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(pages)}</body></html>"
        f = f"{LAY}/katalog.html"; open(f, "w").write(doc)
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--allow-file-access-from-files", "--no-pdf-header-footer",
                        "--virtual-time-budget=8000", f"--print-to-pdf={V}/katalog-modulowy-v11.pdf", "file://" + f], check=True, capture_output=True)
        print("pdf")
