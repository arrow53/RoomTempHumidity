"""Independent check of exported STEP and STL deliverables, not generator state."""
from pathlib import Path
import math,json
import cadquery as cq
import trimesh
root=Path(__file__).resolve().parent
names=['front_bezel','vented_body','rear_cover_radio_mount','rear_cable_strip','side_stand_print_two','fastener_coupon']
report={}
for n in names:
    s=cq.importers.importStep(str(root/(n+'.step'))).val()
    m=trimesh.load_mesh(root/(n+'.stl'))
    assert s.isValid() and len(s.Solids())==1
    assert m.is_watertight and m.is_winding_consistent and m.volume>0
    relative=abs(m.volume-s.Volume())/s.Volume()
    assert relative<.002,(n,relative)
    report[n]={'step_valid':True,'stl_watertight':True,'step_stl_volume_relative_error':relative}
assembly=cq.importers.importStep(str(root/'assembled_enclosure.step')).val()
assert len(assembly.Solids())==6
front=assembly.Solids()[0]
face=max(front.Faces(),key=lambda f:f.Area())
normal=face.normalAt()
angle=math.degrees(math.acos(abs(normal.z)))
assert abs(angle-75)<1e-6,angle
# Positive horizontal shift with rising face height verifies BACKWARD, not forward tilt.
assert normal.y*normal.z<0
report['assembled_step']={'solid_count':6,'front_face_above_desk_deg':angle,'leans_backward':True,'valid':assembly.isValid()}
(root/'export-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
