# Image provenance

- pi-dashboard-current.png: direct unedited capture of the running Pi's Wayland
  display using its existing grim utility, 2026-10-11. Actual live-mode dashboard.
  Visually checked: no credentials, device IDs or private network addresses.
  Displayed readings, local time/timezone and a generic room label remain visible.
- sensor-housing-A2.png: native OpenSCAD rendering of the locally authored sensor
  housing/stand. Prototype visualization, not physical-fit evidence.
- sensor-pcb-A3-copper.png: current A3 CAM top-copper view of locally authored PCB
  geometry, with no third-party component model geometry.

- sensor-pcb-A3-populated.png: native KiCad 10.0.7 ray-traced oblique render generated
  on 2026-10-11 from a temporary copy of the canonical A3 board. Token comparison
  after removing added model records proved all board geometry/placements unchanged.
  Sixteen populated references have models; J2 is intentionally unpopulated.
  The module is an independently authored 9.5 × 13.7 × 1.8 mm nominal body with an
  illustrative shield/antenna-end region. The SHT40 and fuse use existing authored
  dimension-based simplified models. Other packages use official KiCad models;
  dimensions, markings and tolerances are not manufacturer-qualified.

KiCad's [library license exception](https://www.kicad.org/libraries/license/) permits
electronic designs and generated project files using its library data without
requiring the output to inherit the library license. Only the generated PNG is
published here, not a model/library collection.

The supplied original vendor-model render was not reused: a separate publication
grant for the Raytac STEP asset was not established from its local package. Its STEP
and the original bundled render remain excluded. The new image uses no Raytac STEP.
Nominal module dimensions come from the
[manufacturer datasheet](https://www.raytac.com/download/index.php?index_id=74).
No image is AI-generated, and no board routing or manufacturing geometry changed.
