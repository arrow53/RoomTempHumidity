"""Read-only hardware references; updates only local fit report and generated CAD.
Run with --nordic-root <PCA10056...3_0_3 directory> --pi-step <official no-graphics STEP>.
Source files stay outside this repository and are not copied into deliverables.
"""
import argparse,csv,io,json,math,re,runpy,hashlib
from pathlib import Path
import cadquery as cq
parser=argparse.ArgumentParser()
parser.add_argument('--nordic-root',type=Path,required=True)
parser.add_argument('--pi-step',type=Path,required=True)
a=parser.parse_args();root=Path(__file__).resolve().parent
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.stl')}
g=runpy.run_path(str(root/'enclosure.py'))
box=g['box'];local=g['local'];report={'hardware':g['checks']['hardware_configuration']}
prod=a.nordic_root/'Production files'
drill=prod/'DRILL'/'400236-RoundHoles.TXT'
text=drill.read_text();assert 'T08F00S00C0.1260' in text
block=text.split('\nT08\n')[1].split('M30')[0]
x=y=None;holes=[]
for line in block.splitlines():
 for axis,n in re.findall(r'([XY])(-?\d+)',line):
  if axis=='X':x=int(n)*.00254
  else:y=int(n)*.00254
 if x is not None and y is not None:holes.append((x,y))
for h in g['DK_HOLES']:assert any(math.dist(h,p)<.0001 for p in holes),h
outline=(prod/'GERBER'/'400236.GM1').read_text()
assert 'X53750Y4000D01*' in outline and 'Y25000' in outline
report['radio_reference']={'revision':'3.0.3','selected_holes_mm':g['DK_HOLES'],'nominal_hole_diameter_mm':3.2004,'outline_max_mm':[136.525,63.5],'thickness_mm':1.6,'thickness_evidence':'400236_PCB_Laminate_Specification.pdf p1: nominal ~1.6mm, layer-stack sum 1.546mm','source_sha256':{str(p.relative_to(a.nordic_root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [drill,prod/'GERBER'/'400236.GM1',prod/'ASSEMBLY'/'400236_Assembly_Drawing.pdf']}}
pnp=(prod/'PICK_PLACE'/'400236_Pick_And_Place.csv').read_text(encoding='cp1252')
rows=list(csv.DictReader(io.StringIO(pnp[pnp.index('"Designator"'):])));by={r['Designator']:r for r in rows}
report['radio_controls']={n:{'centre_board_mm':[float(by[n]['Center-X(mm)']),float(by[n]['Center-Y(mm)'])],'access':'rear cover removed; component side faces display'} for n in ['J2','J3','SW1','SW2','SW3','SW4','SW5','SW6','SW7','SW8','SW9']}
assert math.dist(report['radio_controls']['J2']['centre_board_mm'],(3.318,31.75))<.0001
assert math.dist(report['radio_controls']['J3']['centre_board_mm'],(89.7293,4.9311))<.0001
# Exact official STEP bounds dominate every component in the supplied model.
pi=cq.importers.importStep(str(a.pi_step)).val();b=pi.BoundingBox()
origin=(60.98,40.62,17.19) # preferred ports-right pose, original display M2.5 mounts
pi_bounds=[b.xmin+origin[0],b.ymin+origin[1],b.zmin+origin[2],b.xmax+origin[0],b.ymax+origin[1],b.zmax+origin[2]]
pi_box=box(*pi_bounds[:3],*[pi_bounds[i+3]-pi_bounds[i] for i in range(3)])
report['bare_pi']={'official_step_sha256':hashlib.sha256(a.pi_step.read_bytes()).hexdigest(),'source_solid_count':len(pi.Solids()),'official_model_bounds_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax],'preferred_pose_translation_mm':origin,'mounted_bounds_mm':pi_bounds,'ports_orientation':'USB-A and Ethernet toward case right, USB-C toward case lower edge','radio_component_gap_mm':74.4-pi_bounds[5],'unused_depth_to_old_reserve_mm':55-pi_bounds[5],'caveat':'Vendor model is guidance only. Original display mounting pose must match this ports-right orientation; FFC and actual plugs are not represented.'}
# Connector boot and bend reservations, not fabricated connector CAD.
# 25mm projection + 10mm bend allowance. Cable bend radius remains supplier-specific.
lanes={
 'bare_pi_official_model_bounds':pi_box,
 'DK_J2_left_plug_25mm':box(17,63.75,86,25,16,8.4),
 'DK_J2_left_bend_allowance':box(7,63.75,76,10,16,18.4),
 'DK_J2_left_down_route':box(7,20,76,10,43.75,10),
 'DK_J3_bottom_plug_25mm':box(123.7293,15,86,16,25,8.4),
 'DK_J3_bottom_bend_allowance':box(123.7293,5,76,16,10,18.4),
 'Pi_USB_C_lower_plug_25mm':box(64.18,15.62,17.6,16,25,10),
 'Pi_USB_C_bend_allowance':box(64.18,5.62,17.6,16,10,20),
 'Pi_USB_A_right_plug_25mm':box(149.030001,61,17,25,36,19),
 'Pi_USB_A_right_bend_allowance':box(174.030001,61,17,10,36,29),
}
report['case_intersection_volumes_mm3']={}
for n,s in lanes.items():
 for pn,part in local.items():
  vol=s.intersect(part).Volume();report['case_intersection_volumes_mm3'][n+' / '+pn]=round(vol,7)
  assert vol<1e-5,(n,pn,vol)
# Nominal ventilation aperture areas from actual construction parameters.
report['ventilation']={'lower_shell_slots':54,'upper_shell_slots':54,'nominal_open_area_each_upper_lower_mm2':54*3*23,'rear_slots':21,'nominal_rear_vent_area_mm2':21*3*22,'side_vents':'partially obscured by side supports; do not count toward minimum free area','cooler':'none','thermal_test':'not performed; passive operation must be monitored under intended load'}
report['fasteners']={'insert_pilot_diameter_mm':4.0,'effective_blind_depth_mm':6.1,'insert_max_length_mm':5.5,'required_insert_confirmation':'Exact maker/part number with specified 4.0mm pilot and length <=5.5mm, then coupon test; M3 thread alone is insufficient. Common 5.7mm inserts are not approved by this current specification.','front_screws':'M3x8: nominal 4mm penetration, 2.1mm bottom clearance','rear_screws':'M3x8: nominal 5mm penetration, 1.1mm bottom clearance','DK_washers':'one under external screw head and one under component-side nut; NO washer between PCB and tower','DK_nuts':'M3 nylon; outer washer diameter <=6mm; check real landing zones'}
assert 8-4 <= 5.5 and 6.1-(8-4)>1
assert 8-3 <= 5.5 and 6.1-(8-3)>1
report['print_release']='HOLD full-case print until exact insert, H2D Pro slicer preview and actual USB plug/bend checks are confirmed. Coupon can be inspected/printed first with a correct printer profile.'
report['cabling']={'external':'Pi power only through single split exit','internal':'DK to Pi USB; actual service-loop sweep requires dry fit'}
report['printer']='Bambu Lab H2D Pro, user confirmed; slicer preview not performed'
report['stl_sha256_unchanged']={p.name:before.get(p.name)==hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.stl')}
assert all(report['stl_sha256_unchanged'].values())
(root/'confirmed-hardware-fit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'fit':'PASS within stated envelopes and preferred pose','bare_pi':report['bare_pi'],'unchanged_stls':report['stl_sha256_unchanged'],'print_release':report['print_release']},indent=2))
