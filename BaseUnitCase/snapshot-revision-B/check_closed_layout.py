"""Analytic envelope checks; does not substitute for installed-board CAD."""
from pathlib import Path
import json,math,struct
root=Path(__file__).resolve().parents[1]/'outputs'/'revision-B'
s=math.sqrt(.5)
def convex_overlap(A,B):
 for P in (A,B):
  for p,q in zip(P,P[1:]+P[:1]):
   axis=(q[1]-p[1],p[0]-q[0])
   va=[x*axis[0]+y*axis[1] for x,y in A];vb=[x*axis[0]+y*axis[1] for x,y in B]
   if min(max(va),max(vb))-max(min(va),min(vb))<=1e-6:return False
 return True
def footprint(Y0,Y1,Z0,Z1):
 return [(30+s*(y+z),100+s*(y-z)) for y,z in [(Y0,Z0),(Y1,Z0),(Y1,Z1),(Y0,Z1)]]
b=(root/'feet_45_print_two.stl').read_bytes();n=struct.unpack_from('<I',b,80)[0]
foottris=[]
for i in range(n):
 a=struct.unpack_from('<12fH',b,84+50*i);pts=[a[j:j+3] for j in (3,6,9)]
 if all(abs(p[2])<1e-6 for p in pts):foottris.append([(p[0],p[1]) for p in pts])
envelopes={'bezel_perimeter':footprint(0,137.24,0,4),'side_walls':footprint(0,137.24,4,110),'rear_cover':footprint(0,137.24,110,113),'stand_tab':footprint(-16,0,0,6)}
checks={name:not any(convex_overlap(P,T) for T in foottris) for name,P in envelopes.items()}
assert all(checks.values()),checks
dkholes=[(48+13.97,40+7.62),(48+15.24,40+55.88),(48+66.04,40+12.70)]
for x,y in dkholes:
 for vx in range(130,190,9):
  for vy in (26,62,98):
   assert x+4<=vx or x-4>=vx+3 or y+4<=vy or y-4>=vy+24
checks['radio_mounts_do_not_intersect_rear_vents']=True
checks['radio_outline_inside_shell_xy']=48+136.525<203.32 and 40+63.5<134.24
checks['radio_component_gap_above_assumed_pi_envelope_mm']=66.4-55
checks['rear_cover_lower_corner_desk_gap_mm']=100-s*113
checks['all_part_bounds_fit_conservative_300x320x325_build_envelope']=True
report=json.loads((root/'mesh-checks.json').read_text())
for name,data in report.items():
 if 'bounds_mm' not in data:continue
 dims=[b-a for a,b in data['bounds_mm']]
 assert dims[0]<300 and dims[1]<320 and dims[2]<325,(name,dims)
checks['limitation']='Envelope and profile checks only. Exact installed hardware, cable solids, tip stability, thermal and RF fit remain untested.'
(root/'layout-checks.json').write_text(json.dumps(checks,indent=2))
print(json.dumps(checks,indent=2))
