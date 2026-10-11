"""Revision C, millimetres. Run with CadQuery 2.8 and trimesh 5.1.
Parametric master; no legacy paths. Outputs alongside this file.
Display face: 75 degrees above desk / 15 degrees back from vertical.
Hardware proxies are clearance envelopes, not vendor component CAD.
"""
from pathlib import Path
import math, json, itertools
import cadquery as cq
import trimesh
OUT=Path(__file__).resolve().parent
W,H,D=206.32,137.24,120.0
ANGLE=75.0
C,S=math.cos(math.radians(ANGLE)),math.sin(math.radians(ANGLE))
Y0,Z0=30.0,45.0
RADIO_X,RADIO_Y=42.0,40.0
RADIO_STANDOFF=24.0
DK_HOLES=[(13.97,7.62),(15.24,55.88),(66.04,12.70)]
FOOT_FRONT,FOOT_REAR,FOOT_T=-35.0,205.0,12.0
MOUNTS=[(20.,60.),(75.,60.)] # y,z in enclosure coordinates
corners=[(4.,4.),(W-4,4.),(4.,H-4),(W-4,H-4)]
rear_screws=corners+[(4.,22.),(W-4,22.)]
V=cq.Vector

def box(x,y,z,dx,dy,dz):return cq.Solid.makeBox(dx,dy,dz,V(x,y,z))
def cyl(x,y,z,r,h,axis=(0,0,1)):return cq.Solid.makeCylinder(r,h,V(x,y,z),V(*axis))
def union(shapes):
    return shapes[0].fuse(*shapes[1:]).clean() if len(shapes)>1 else shapes[0]
def cut(a,shapes):return a.cut(*shapes).clean()
def world(sh):return sh.mirror('XY').rotate((0,0,0),(1,0,0),ANGLE).translate((0,Y0,Z0))
def yz(y,z):return (Y0+C*y+S*z,Z0+S*y-C*z)
def hex_x(x,y,z,af,length):
    r=af/math.sqrt(3)
    return cq.Workplane('YZ',origin=(x,y,z)).polyline([(r*math.cos(a*math.pi/3),r*math.sin(a*math.pi/3)) for a in range(6)]).close().extrude(length).val()

parts={}
# Glass pocket and compliant front lip. Body seats on bezel, never on glass.
bezel=cut(box(0,0,0,W,H,4),[box(11,11,-1,W-22,H-22,7),box(8,8,1.8,190.32,121.24,5)]+[cyl(x,y,-1,1.7,7) for x,y in corners])
parts['front_bezel']=bezel
# Body is specified in assembled local coordinates z=4..120.
a=[box(0,0,4,W,H,3),box(0,0,4,3,H,D-4),box(W-3,0,4,3,H,D-4),box(0,0,4,W,3,D-4),box(0,H-3,4,W,3,D-4)]
a += [box(x-4,y-4,4,8,8,D-4) for x,y in corners]
a += [box(x-4,y-4,D-10,8,8,10) for x,y in rear_screws[4:]]
# Full-height roots from the print bed avoid unsupported internal bolt bosses.
for x in (0,W-12):
    for y,z in MOUNTS:a.append(box(x,y-8,4,12,16,z+8-4))
c=[box(11,11,3,W-22,H-22,5)]
c += [cyl(x,y,3.9,2.,6.2) for x,y in corners] # M3 insert pilot, exact insert to be selected
c += [cyl(x,y,D-6.1,2.,6.2) for x,y in rear_screws]
for x in range(18,190,10):
    for z in (18,51,84):c += [box(x,-1,z,3,5,23),box(x,H-4,z,3,5,23)]
for y in range(32,124,12):
    # Leave continuous material around both stand mounting roots.
    if 64<=y<=84:continue
    c += [box(-1,y,28,5,3,35),box(W-4,y,28,5,3,35)]
for y,z in MOUNTS:
    c += [cyl(-1,y,z,2.2,14,(1,0,0)),cyl(W-13,y,z,2.2,14,(1,0,0))]
    # Standard M4 nuts, 7.2 mm AF recess, 3.4 mm deep, accessible from interior.
    c += [hex_x(8.6,y,z,7.2,4.0),hex_x(W-12.6,y,z,7.2,4.0)]
body=cut(union(a),c)
parts['vented_body']=body.translate((0,0,-4))
# Removable rear cover, outer face at print z=0, towers pointing up.
a=[box(0,14.3,0,W,H-14.3,3)]
for x,y in DK_HOLES:a.append(cyl(RADIO_X+x,RADIO_Y+y,3,3.2,RADIO_STANDOFF))
c=[cyl(x,y,-1,1.7,6) for x,y in rear_screws if y!=4]
c += [cyl(RADIO_X+x,RADIO_Y+y,-1,1.7,RADIO_STANDOFF+6) for x,y in DK_HOLES]
for x in range(128,190,9):
    for y in (29,65,101):c.append(box(x,y,-1,3,22,5))
# One 24 x 12 split exit for Pi power only; DK USB remains internal.
for x in (62,):c.append(box(x,13.5,-1,24,6.5,5))
for x in (26,40,65,79):c.append(box(x,24,-1,3,8,5))
cover=cut(union(a),c)
parts['rear_cover_radio_mount']=cover
strip=cut(box(0,0,0,W,14,3),[cyl(x,4,-1,1.7,5) for x in (4,W-4)]+[box(x,8,-1,24,7,5) for x in (62,)])
parts['rear_cable_strip']=strip
# Feet are a bolted side plate / desk runner, not a gravity-fit slot.
m0,m1=[yz(y,z) for y,z in MOUNTS]
poly=[(FOOT_FRONT,0),(FOOT_REAR,0),(FOOT_REAR,7),(m1[0]+15,m1[1]+14),(m1[0]-14,m1[1]+14),(FOOT_FRONT,7)]
foot=cq.Workplane('YZ').polyline(poly).close().extrude(FOOT_T).val()
foot=cut(foot,[cyl(-1,y,z,2.2,FOOT_T+2,(1,0,0)) for y,z in (m0,m1)])
# Foot STL lies broad face down, thickness in print Z. One shape, print two.
foot_print=foot.rotate((0,0,0),(0,1,0),90).rotate((0,0,0),(0,0,1),90)
bb=foot_print.BoundingBox();foot_print=foot_print.translate((-bb.xmin,-bb.ymin,-bb.zmin))
parts['side_stand_print_two']=foot_print
coupon=cut(box(0,0,0,45,24,8),[cyl(6,12,-1,1.7,10),cyl(17,12,1.9,2,7),cyl(28,12,-1,2.2,10),hex_x(-1,12,4,7.2,4.4)])
parts['fastener_coupon']=coupon
# Assemble exact manufacturing geometry.
local={'front_bezel':bezel,'vented_body':body,'rear_cover_radio_mount':cover.mirror('XY').translate((0,0,D+3)),'rear_cable_strip':strip.mirror('XY').translate((0,0,D+3))}
assembly={k:world(v) for k,v in local.items()}
assembly['stand_left']=foot.translate((-FOOT_T,0,0));assembly['stand_right']=foot.translate((W,0,0))
# Hardware reserve volumes; Pi is intentionally a broad placement envelope.
# Broad reserve for Pi mounting orientations and cooler; cable plugs are separate allowances.
hardware={
 'display_glass':box(8.5,8.5,2.3,189.32,120.24,.7),
 'display_rear_reserve':box(15.84,18.265,3.,175.14,99.71,14.22),
 'pi_and_cooler_reserve':box(38,30,17.22,127,80,37.78),
 'radio_pcb_reserve':box(RADIO_X,RADIO_Y,94.4,136.525,63.5,1.6),
 'radio_components_reserve':box(RADIO_X,RADIO_Y,74.4,136.525,63.5,20),
 'radio_underside_reserve':box(RADIO_X,RADIO_Y,96,136.525,63.5,20),
 'antenna_keep_clear':box(RADIO_X+115,RADIO_Y,74.4,21.525,63.5,41.6),
 'radio_usb_service':box(7,RADIO_Y+22,77,35,24,18),
 'pi_side_cable_lane':box(13,35,25,25,70,38),
}
# Glass real corners R8; rear reserve only is rectangular conservative proxy.
hardware['display_glass']=cq.Workplane(obj=hardware['display_glass']).edges('|Z').fillet(8).val()
# Record the booleans that matter, excluding designed contacts and proxy overlap.
checks={'units':'mm','angle_above_horizontal_deg':ANGLE,'back_from_vertical_deg':90-ANGLE,'digital_only':True}
checks['printer']={'model':'Bambu Lab H2D Pro, user confirmed','slicer_validation':'not performed'}
checks['cabling']={'external':'Pi USB-C power supply only','internal':'DK USB to Pi USB-A, with rear-cover service loop','power_exit_mm':[24,12],'power_exit_count':1}
checks['hardware_configuration']={'computer':'Raspberry Pi 5 8GB','cooler':'none, user confirmed','radio':'nRF52840 DK PCA10056 revision 3.0.3','board_marking':'2026.21, reported by user; not interpreted as a revision','hardware_fit_status':'digital checks only; actual cable plugs and inserts remain unconfirmed'}
checks['parts']={}
for name,shape in parts.items():
    assert shape.isValid(),name
    assert len(shape.Solids())==1,(name,'disconnected solid')
    cq.exporters.export(shape,str(OUT/(name+'.step')))
    cq.exporters.export(shape,str(OUT/(name+'.stl')),tolerance=.06,angularTolerance=.1)
    mesh=trimesh.load_mesh(OUT/(name+'.stl'),process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0,name
    b=shape.BoundingBox()
    checks['parts'][name]={'valid_brep':True,'solids':1,'watertight_mesh':True,'consistent_winding':True,'triangles':len(mesh.faces),'bounds_mm':[b.xlen,b.ylen,b.zlen],'volume_mm3':shape.Volume()}
    print('Exported',name,flush=True)
checks['assembly_intersections_mm3']={}
for (a,A),(b,B) in itertools.combinations(assembly.items(),2):
    v=A.intersect(B).Volume();checks['assembly_intersections_mm3'][a+' / '+b]=round(v,7)
    assert v<1e-5,(a,b,v)
checks['hardware_clearances']={}
for h in ('display_glass','display_rear_reserve','pi_and_cooler_reserve','radio_pcb_reserve','radio_components_reserve','radio_usb_service','pi_side_cable_lane'):
    env=hardware[h]
    for n,p in local.items():
        v=env.intersect(p).Volume()
        checks['hardware_clearances'][h+' / '+n]=round(v,7)
        assert v<1e-5,(h,n,v)
# Underside envelope allows its intended three slender mounting towers.
under=hardware['radio_underside_reserve']
allowed=union([cyl(RADIO_X+x,RADIO_Y+y,95.9,3.21,25) for x,y in DK_HOLES])
assert under.cut(allowed).intersect(local['rear_cover_radio_mount']).Volume()<1e-5
checks['radio_underside_clear_except_mount_landing_zones']=True
checks['glass_pocket_side_clearance_mm']=.5
checks['padded_glass_stack_mm']={'available':2.2,'nominal_glass':.7,'front_pad':.5,'rear_pad':.5,'nominal_free':.5}
checks['pi_radio_component_gap_mm']=74.4-55
checks['antenna_to_display_rear_depth_gap_mm']=74.4-17.22
checks['antenna_to_rear_plastic_mm']=120-116
checks['radio_left_usb_straight_lane_mm']=35
checks['case_lowest_desk_clearance_mm']=yz(0,D+3)[1]
checks['support_polygon_mm']=[[-FOOT_T,FOOT_FRONT],[W+FOOT_T,FOOT_FRONT],[W+FOOT_T,FOOT_REAR],[-FOOT_T,FOOT_REAR]]
checks['maximum_print_part_xyz_mm']=[max(d['bounds_mm'][i] for d in checks['parts'].values()) for i in range(3)]
# Conservative geometry-only COM bracket: shell, feet and hardware reserves lie
# inside this interval. Nominal mass model assumes 45% solid PETG effective density.
masses=[]
for name,shape in assembly.items():masses.append((shape.Volume()*1.27e-6*.45,shape.Center().toTuple(),name))
for name,mass in [('display_glass',.3),('pi_and_cooler_reserve',.05),('radio_pcb_reserve',.045)]:masses.append((mass,world(hardware[name]).Center().toTuple(),name))
masses.append((.05,world(box(20,25,45,100,40,30)).Center().toTuple(),'cables_fasteners_allowance'))
total=sum(m for m,p,n in masses);com=[sum(m*p[i] for m,p,n in masses)/total for i in range(3)]
margins=[com[0]+FOOT_T,W+FOOT_T-com[0],com[1]-FOOT_FRONT,FOOT_REAR-com[1]]
top=yz(H,0)[1]
checks['stability_estimate']={'assumptions':'45% effective solid PETG; display 300g; bare Pi 50g estimate; DK45g; wires50g. Measure actual mass/COM. Pads friction untested.','mass_kg':total,'com_xyz_mm':com,'edge_margins_mm':margins,'horizontal_tip_force_at_screen_top_N':total*9.81*min(margins)/top,'screen_top_mm':top,'measured':False}
assert min(margins)>40
# Service path: rear cover with DK withdraws along local +Z. Case body does not obstruct.
withdrawal=union([local['rear_cover_radio_mount'],hardware['radio_pcb_reserve'],hardware['radio_components_reserve']])
for dist in (5,15,35,60,100):assert withdrawal.translate((0,0,dist)).intersect(body).Volume()<1e-5
checks['rear_cover_removal_clearance_sampled_mm']=[5,15,35,60,100]
# Assembly export is enclosure-only; hardware proxies are kept in separately labelled STEP.
cq.exporters.export(cq.Compound.makeCompound(list(assembly.values())),str(OUT/'assembled_enclosure.step'))
cq.exporters.export(cq.Compound.makeCompound([world(s) for s in hardware.values()]),str(OUT/'hardware_clearance_PROXIES.step'))
(OUT/'validation.json').write_text(json.dumps(checks,indent=2))
# Actual CAD tessellation, shared with software renderer; no image-generation geometry.
colors={'front_bezel':[40,55,65],'vented_body':[106,125,133],'rear_cover_radio_mount':[46,63,74],'rear_cable_strip':[198,132,59],'stand_left':[51,68,79],'stand_right':[51,68,79]}
scene=[]
def scene_add(name,shape,color):
    vs,fs=shape.tessellate(.08,.12)
    scene.append({'name':name,'vertices':[v.toTuple() for v in vs],'faces':fs,'color':color})
for n,s in assembly.items():scene_add(n,s,colors[n])
scene_add('glass',world(hardware['display_glass']),[12,17,23])
scene_add('inactive_screen',world(box((W-154.56)/2,(H-86.94)/2,2.27,154.56,86.94,.025)),[20,49,59])
# Screw heads shown at the actual clearance-hole centres, no heads over the active view.
for x,y in corners:scene_add('bezel_M3_head',world(cyl(x,y,-1.8,2.85,1.8)),[25,29,33])
for x,y in rear_screws:scene_add('rear_M3_head',world(cyl(x,y,D+3,2.85,1.8)),[25,29,33])
for x,y in DK_HOLES:scene_add('nylon_radio_head',world(cyl(RADIO_X+x,RADIO_Y+y,D+3,2.8,2)),[189,193,184])
for y,z in (m0,m1):
    scene_add('left_M4_head',cyl(-FOOT_T-2.5,y,z,3.8,2.5,(1,0,0)),[24,29,33])
    scene_add('right_M4_head',cyl(W+FOOT_T,y,z,3.8,2.5,(1,0,0)),[24,29,33])
(OUT/'render_scene.json').write_text(json.dumps(scene,separators=(',',':')))
print('PASS: B-reps, STL topology, assembly collision checks, clearance envelopes, sampled rear extraction, tilt and analytical stability',flush=True)
