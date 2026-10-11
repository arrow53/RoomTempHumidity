"""Inspect binary STL topology without installing dependencies. Not a slicer or physical fit test."""
from pathlib import Path
import collections
import hashlib
import json
import math
import struct
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
OUT = ROOT
EXPECTED = {'usb_wall': (32,20,23.6), 'pcb_boss': (11,12,6.4), 'pcb_shim': (11,12,1.6), 'case_nut': (11,12,23.6), 'case_lid': (11,12,4.8)}

def inspect(name, dimensions):
    path = OUT / (name + '_PROVISIONAL.stl')
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    if len(data) != 84 + 50 * count:
        raise ValueError(f'{name}: expected a complete binary STL')
    vertices, index, faces = [], {}, []
    for i in range(count):
        row = struct.unpack_from('<12fH', data, 84 + i * 50)
        face = []
        for j in (3, 6, 9):
            key = tuple(row[j:j+3])
            if not all(math.isfinite(x) for x in key):
                raise ValueError('Nonfinite vertex')
            if key not in index:
                index[key] = len(vertices)
                vertices.append(key)
            face.append(index[key])
        faces.append(tuple(face))
    edges = collections.defaultdict(list)
    vertex_faces = collections.defaultdict(set)
    degenerate = 0
    volume = 0.0
    for i, (a, b, c) in enumerate(faces):
        va, vb, vc = vertices[a], vertices[b], vertices[c]
        ab = tuple(vb[j] - va[j] for j in range(3))
        ac = tuple(vc[j] - va[j] for j in range(3))
        cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
        if len({a,b,c}) < 3 or sum(x*x for x in cross) < 1e-16:
            degenerate += 1
        volume += (va[0]*(vb[1]*vc[2]-vb[2]*vc[1]) + va[1]*(vb[2]*vc[0]-vb[0]*vc[2]) + va[2]*(vb[0]*vc[1]-vb[1]*vc[0])) / 6
        for u,v in ((a,b),(b,c),(c,a)):
            edges[tuple(sorted((u,v)))].append((i, u < v))
        for v in (a,b,c): vertex_faces[v].add(i)
    adjacency = [set() for _ in faces]
    winding_errors = 0
    for incidents in edges.values():
        if len(incidents) == 2:
            (a,da),(b,db) = incidents
            adjacency[a].add(b); adjacency[b].add(a)
            winding_errors += da == db
    unseen = set(range(len(faces)))
    components = 0
    while unseen:
        components += 1
        queue = [unseen.pop()]
        while queue:
            for other in adjacency[queue.pop()]:
                if other in unseen:
                    unseen.remove(other); queue.append(other)
    fan_errors = 0
    for v, incident in vertex_faces.items():
        found = {next(iter(incident))}; queue = list(found)
        while queue:
            for other in adjacency[queue.pop()] & incident:
                if other not in found: found.add(other); queue.append(other)
        fan_errors += found != incident
    mins = [min(v[j] for v in vertices) for j in range(3)]
    maxs = [max(v[j] for v in vertices) for j in range(3)]
    extents = [b-a for a,b in zip(mins,maxs)]
    bad_edges = sum(len(v) != 2 for v in edges.values())
    checks = {'every_edge_has_two_faces': bad_edges == 0, 'consistent_winding': winding_errors == 0,
              'connected_vertex_fans': fan_errors == 0, 'no_degenerate_triangles': degenerate == 0,
              'single_connected_component': components == 1, 'positive_signed_volume': volume > 0,
              'expected_dimensions': all(abs(a-b) < 0.01 for a,b in zip(extents,dimensions))}
    return {'part': name, 'file': path.name, 'sha256': hashlib.sha256(data).hexdigest(),
            'triangles': count, 'vertices': len(vertices), 'components': components,
            'bad_edge_count': bad_edges, 'winding_error_count': winding_errors,
            'vertex_fan_error_count': fan_errors, 'degenerate_count': degenerate,
            'bounds_mm': [mins,maxs], 'dimensions_mm': extents, 'signed_volume_mm3': volume,
            'checks': checks, 'passed': all(checks.values())}

# Same topology checks as the A2 part validator; no edits or repairs to STL files.
results = [inspect(name, size) for name, size in EXPECTED.items()]
OUT = ROOT.parent / 'provisional_cad'
reused = inspect('coupon', (52,14,8))
reused['file'] = '../provisional_cad/coupon_PROVISIONAL.stl'
results.append(reused)
OUT = ROOT
baseline = json.loads((ROOT/'unchanged_geometry_baseline.json').read_text(encoding='utf-8-sig'))
preservation = []
for entry in baseline:
    p = Path(entry['Path'])
    actual = hashlib.sha256(p.read_bytes()).hexdigest()
    preservation.append({'file': str(p), 'unchanged': actual.lower() == entry['Hash'].lower(), 'sha256': actual})
report = {
    'generated_utc': datetime.now(timezone.utc).isoformat(),
    'a2_source_sha256': hashlib.sha256((ROOT.parent/'sensor_enclosure.scad').read_bytes()).hexdigest(),
    'coupon_source_sha256': hashlib.sha256((ROOT/'fit_coupons_generated.scad').read_bytes()).hexdigest(),
    'status': 'PROVISIONAL_PHYSICAL_FIT_NOT_VERIFIED',
    'all_six_meshes_passed': all(r['passed'] for r in results),
    'original_geometry_and_interfaces_unchanged': all(p['unchanged'] for p in preservation),
    'scope': 'Binary STL topology, dimensions, connectivity and signed volume; five new solids plus existing nut coupon reused in place. No independent self-intersection, slicing or physical tests.',
    'parts': results,
    'preservation': preservation
}
(ROOT/'mesh_validation.json').write_text(json.dumps(report,indent=2), encoding='utf-8')
for result in results:
    print(result['part'], 'PASS' if result['passed'] else 'FAIL', [round(x,4) for x in result['dimensions_mm']])
print('Original geometry/interfaces unchanged:', report['original_geometry_and_interfaces_unchanged'])
if not report['all_six_meshes_passed'] or not report['original_geometry_and_interfaces_unchanged']:
    raise SystemExit(1)
