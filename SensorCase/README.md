# Sensor enclosure A2

Editable OpenSCAD source, five provisional primary STL parts and cropped fit coupons.
The static validator uses the preserved PCB A1 mechanical snapshot for its geometry;
the current PCB A3 documentation reports unchanged outline and component placements.
Physical fit, strength, RF and thermal validation remain open. No manufacturing release.

Use `validate_concept.ps1` and `python inspect_enclosure_meshes.py` for static/mesh
checks. They generate local JSON reports. These checks do not prove printed fit.
Rendering/collision scripts accept `-OpenScadPath` or `OPENSCAD_EXE`, or find
`openscad.com` on PATH. OpenSCAD 2021.01 was the original verified renderer.
No OpenSCAD binary is bundled. The scripts explicitly enable provisional rendering
without changing the source approval flags. Review outputs before replacing print files.

Read HARDWARE_AND_ASSEMBLY.md and fit_coupons/PRINT_AND_MEASURE.md before printing.
Keep the prototype RF/thermal reservations and test the actual USB cable and fasteners.
