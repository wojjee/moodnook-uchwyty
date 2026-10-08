import sys, json
sys.path.insert(0, '/workspace/moodnook/ai-design')
from nookcad import *
bar, post, wash, col = (bar_OB(128), make_post('SR7', 30), make_washer('WR12'), make_collar(8, 8, 'R'))
d_lo, wall, d_up = joint_depths(post, bar, col)
Ls, lo, up = pick_stud(d_lo, wall, d_up, eng_up=SYS['ENG_MIN'] + 1.0)
stud, screw = (m4_stud(Ls), m4_screw(25))
g = 13.0
A = Assy('EXPLODED_OB-R128')
z = {}
z['screw'] = 0.0
z['washer'] = 25 + g
z['post'] = z['washer'] + wash.meta['t'] + g
z['stud'] = z['post'] + post.meta['H'] + g
z['collar'] = z['stud'] + Ls + g
z['bar'] = z['collar'] + col.meta['f'] + g
cc = 128
for x, s in ((-cc / 2, 'L'), (cc / 2, 'R')):
    A.add(screw, Pos(x, 0, z['screw']), 'screw' + s)
    A.add(wash, Pos(x, 0, z['washer']), 'w' + s)
    A.add(post, Pos(x, 0, z['post']), 'p' + s)
    A.add(stud, Pos(x, 0, z['stud']), 'stud' + s)
    A.add(col, Pos(x, 0, z['collar']), 'c' + s)
A.add(bar, Pos(0, 0, z['bar']), 'bar')
A.meta = dict(sku=f'{bar.code}/{post.code}/{wash.code}/{col.code}/SB.PB')
info = export_assy(A, '/workspace/moodnook/v11/step/SYS/exploded')
lift = 4.0
xr = cc / 2
anchors = {'bar': [-20, 0, z['bar'] + 4 + lift], 'collar': [xr + 5.0, 0, z['collar'] + col.meta['f'] + lift], 'stud': [xr + 2.2, 0, z['stud'] + Ls / 2 + lift], 'post': [xr + 3.6, 0, z['post'] + 15 + lift], 'washer': [xr + 6.0, 0, z['washer'] + 0.5 + lift], 'screw': [xr + 2.0, 0, z['screw'] + 10 + lift]}
labels = {'bar': (f'Pręt {bar.code}', f"Ø{bar.meta['rod_d']:g} mm, mosiądz satynowy-mat, 2× M4 gwint promieniowy (gł. {bar.meta['tap_depth']:g})"), 'collar': (f'Obrączka {col.code}', f"Ø{col.meta['D']:g} × 6, PB, płaska baza {col.meta['land_w']:.1f} mm + otwór Ø4,3"), 'stud': (f'Trzpień M4×{Ls} ISO 4026', f'Loctite 243; wkręcenie {lo:.1f} / {up:.1f} mm'), 'post': (f'Słupek {post.code}', 'Ø7 × 30, M4 z obu stron (gł. 9), kieszeń Ø5,1 w stopie'), 'washer': (f'Podkładka {wash.code}', 'Ø12 × 1, PB, czop Ø5,0 × 1,0'), 'screw': ('Wkręt M4×25', 'od tyłu frontu meblowego w stopę słupka')}
json.dump(dict(info=info, anchors=anchors, labels=labels, lift=lift, z=z, stud=Ls), open('/workspace/moodnook/v11/renders/spec/exploded_meta.json', 'w'), indent=1, ensure_ascii=False)
print(info['files'], Ls, lo, up)
