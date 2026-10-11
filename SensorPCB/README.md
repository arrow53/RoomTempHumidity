# Sensor PCB A3

Current manufacturing revision: **A3-Q10-quote-v1**. These are quote/DFM review
files, not a production release, purchase approval or validated assembled prototype.

Open `editable/room_sensor.kicad_pro`. Its project-local symbols and footprints
travel with the project. `fabrication/` contains selected Gerbers/drills;
`assembly/` contains the ten-board BOM, placements and DNP/board-feature table.
The native CAD and selected manufacturing files were copied unchanged and hash-checked.
Do not regenerate A3 using older A2 construction scripts.

A3 changes the regulator to LT1761IS5-3.3#TRMPBF and its local layout. The 45 x 55 mm
board outline, mounting positions and enclosure interface remain unchanged. Native
ERC/DRC and manufacturing audits passed in the original engineering work; this
publication did not rerun KiCad or qualify physical hardware.

Full original quote ZIPs, third-party datasheets, official vendor 3D models, assembled
STEP exports, historical A2 sources and raw review logs remain outside this snapshot.
No rendered 3D model completeness is implied. Refer to the original full reviewed
quote package before fabrication; USB process/tolerance and programming/test scope
remain open. Additional source/assembly/DFM documents will be included only after
their privacy, completeness and redistribution review.

Project-specific geometry was generated locally. Manufacturer names and part numbers
identify intended components, not supplier certification. Upstream KiCad library or
vendor assets added later retain their own licenses and attribution requirements.
